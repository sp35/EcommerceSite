from django.dispatch import receiver
from allauth.account.signals import user_signed_up
from core.models import Customer


@receiver(user_signed_up)
def generate_customer(sender, **kwargs):
    user = kwargs['user']
    user.is_customer = True
    user.save()
    customer = Customer.objects.create(user=user)