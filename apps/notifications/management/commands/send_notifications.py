import logging
from datetime import timedelta

from django.core.mail import send_mail
from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.rentals.models import RentalOrder
from apps.notifications.email import greeting, plural_days

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Отправка уведомлений об окончании срока аренды и просрочках"

    def handle(self, *args, **options):
        today = timezone.now().date()

        # Напоминания за 30, 14, 7 и 3 дня до окончания аренды
        for days in [30, 14, 7, 3]:
            for order in RentalOrder.objects.filter(
                status="active", end_date=today + timedelta(days=days)
            ):
                try:
                    send_mail(
                        "Заканчивается срок аренды!",
                        f"{greeting(order.user)} срок аренды бокса "
                        f"заканчивается через {days} дней.",
                        None,
                        [order.user.email],
                        fail_silently=False,
                    )
                except Exception:
                    logger.exception(
                        "Не удалось отправить напоминание для заказа %s", order.id
                    )

        # Просроченные: переводим в overdue и напоминаем раз в месяц, начиная с 1-го дня
        for order in RentalOrder.objects.filter(status__in=["active", "overdue"], end_date__lt=today):
            if order.status == "active":
                order.status = "overdue"
            days_overdue = (today - order.end_date).days
            if days_overdue >= 1 and (
                order.last_overdue_notified is None
                or (today - order.last_overdue_notified).days >= 30
            ):
                try:
                    send_mail(
                        "Срок аренды просрочен!",
                        f"{greeting(order.user)} срок аренды бокса №{order.box.number} "
                        f"закончился {days_overdue} {plural_days(days_overdue)} назад.\n\n"
                        f"Ваши вещи будут храниться ещё 6 месяцев по повышенному тарифу. "
                        f"Если вы не заберёте или не продлите аренду в течение этого срока, "
                        f"вещи будут списаны — вы их потеряете.\n\n"
                        f"Пожалуйста, продлите аренду или заберите вещи в личном кабинете.",
                        None,
                        [order.user.email],
                        fail_silently=False,
                    )
                    order.last_overdue_notified = today
                except Exception:
                    logger.exception(
                        "Не удалось отправить письмо о просрочке для заказа %s", order.id
                    )
            order.save()
