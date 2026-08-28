import logging
from datetime import timedelta

from django.core.mail import send_mail
from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.rentals.models import RentalOrder
from apps.notifications.email import greeting

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

        # Просроченные: переводим в overdue и напоминаем ровно один раз — на 1-й день просрочки
        for order in RentalOrder.objects.filter(status="active", end_date__lt=today):
            order.status = "overdue"
            order.save()
            days_overdue = (today - order.end_date).days
            if days_overdue == 1:
                try:
                    send_mail(
                        "Срок аренды просрочен!",
                        f"{greeting(order.user)} срок аренды бокса "
                        f"просрочен на {days_overdue} дней.",
                        None,
                        [order.user.email],
                        fail_silently=False,
                    )
                except Exception:
                    logger.exception(
                        "Не удалось отправить письмо о просрочке для заказа %s", order.id
                    )
