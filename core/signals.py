from django.dispatch import receiver
from django.db.models.signals import post_save
from core.models import Order

import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail


@receiver(post_save, sender=Order)
def send_order_mails(sender, instance, created, **kwargs):
    if created:
        try:
            sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
            sender_email = str(os.environ.get('SENDER_EMAIL'))
            message = Mail(
            from_email=sender_email,
            to_emails=str(instance.items.vendor.user.email),
            subject=f'New order received from {instance.customer.user.username}',
            html_content=f'<strong>{instance.items.quantity} of {instance.items.item.title}</strong>')
            response = sg.send(message)
            print(response.status_code)
            print(response.body)
            print(response.headers)
        except Exception as e:
            print(str(e))