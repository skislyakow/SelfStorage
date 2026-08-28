from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from apps.rentals.models import RentalOrder
from django.core.mail import send_mail

class Command(BaseCommand):

    def handle(self, *args, **options):
        days_list = [30, 14, 7, 3]
        today = timezone.now().date()
        for days in days_list:
            future_date = today + timedelta(days=days)
            orders = RentalOrder.objects.filter(end_date=future_date, status='active')
            for order in orders:
                send_reminder(order, days)

        overdue_orders = RentalOrder.objects.filter(end_date__lt=today, status='active')
        for order in overdue_orders:
            order.status = 'overdue'
            order.save()

        overdue_orders = RentalOrder.objects.filter(status='overdue')
        for order in overdue_orders:
            days_overdue = (today - order.end_date).days
            if days_overdue > 0 and days_overdue % 30 == 0:
                send_overdue_reminder(order, days_overdue)

        six_months_orders = RentalOrder.objects.filter(status='overdue', end_date__lte=today - timedelta(days=180))
        for order in six_months_orders:
            order.status = 'finished'
            order.save()
            send_final_warning(order)


def send_reminder(order, days_left):
    send_mail(
        subject='Заканчивается срок аренды!',
        message=f'Здравствуйте! Хотим вам напомнить что через {days_left} дней заканчивается аренда.',
        from_email=None,
        recipient_list=[order.user.email]
    )

def send_overdue_reminder(order, days_overdue):
    send_mail(
        subject='Срок аренды просрочен!',
        message='Срок аренды бокса просрочен! Последующее хранение по повышенному тарифу в течение 6 месяцев!',
        from_email=None,
        recipient_list=[order.user.email]
    )

def send_final_warning(order):
    send_mail(
        subject='ВНИМАНИЕ: вещи будут утеряны!',
        message=f'Ваши заказы будет утеряны если не продлите аренду бокса!',
        from_email=None,
        recipient_list=[order.user.email]
    )
