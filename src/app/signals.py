import base62
from django.db.models.signals import post_save
from django.dispatch import receiver

from app.tasks import notify_async

from .models import Ping, Service


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


@receiver(post_save, sender=Ping)
def check_ping(sender, instance, created, **kwargs):
    if not created:
        return
    data = instance.data.strip()
    if not data:
        return
    notify_async(instance.service.notify_to.strip().split(";"),
                 instance.service.name,
                 instance.service.tp,
                 instance.service.value,
                 instance.service.grace,
                 data
                 )
