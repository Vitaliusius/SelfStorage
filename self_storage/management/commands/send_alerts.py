from datetime import timedelta
from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.utils import timezone
from self_storage.models import Order

class Command(BaseCommand):


    def handle(self, *args, **options):
        target_date = timezone.now().date() + timedelta(days=3)

        orders = Order.objects.filter(end_date=target_date, status="active").select_related('user')
        
        if not orders.exists():
            return

        for order in orders:
            user = order.user
            if user.email:
                send_mail(
                    subject="Аренда бокса заканчивается!",
                    message=f"Здравствуйте! Напоминаем, что срок аренды бокса заканчивается {order.end_date}.",
                    from_email=None,
                    recipient_list=[user.email],
                    fail_silently=True,
                )
