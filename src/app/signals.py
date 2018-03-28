from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Service
import base62


@receiver(post_save, sender=Service)
def set_service_short_url(sender, instance, created, **kwargs):
    if not created:
        return
    instance.short_url = base62.encode(88888888 + instance.id)
    instance.save()


@receiver(post_save, sender=Service)
def add_first_ping(sender, instance, created, **kwargs):
    if not created:
        return
    instance.pings.create(
        remote_addr='127.0.0.1',
        ua='iphone xxx',
        data=''
    )
