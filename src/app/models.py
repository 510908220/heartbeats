# -*- coding:utf-8 -*-

from django.db import models
from django.conf import settings
# Create your models here.


class Tag(models.Model):
    class Meta:
        db_table = "tag"
    name = models.CharField(max_length=200, unique=True, blank=False, null=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Service(models.Model):
    class Meta:
        db_table = "service"

    STATUS = (
        ('running', 'running'),
        ('stoped', 'stoped'),
    )
    TYPES = (
        ('at', 'at'),
        ('every', 'every'),
    )

    name = models.CharField(max_length=200, unique=True, blank=False, null=False)
    status = models.CharField(choices=STATUS, default=STATUS[0][0], max_length=20)
    tp = models.CharField(choices=TYPES, default=TYPES[0][0], max_length=20)
    value = models.CharField(max_length=200, default='')

    notify_to = models.TextField(default="")

    grace = models.IntegerField(default=0)
    short_url = models.CharField(max_length=200,  unique=True, blank=True, null=True)

    tags = models.ManyToManyField(Tag, related_name='services')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Ping(models.Model):
    class Meta:
        db_table = "ping"
    service = models.ForeignKey(Service, related_name='pings', on_delete=models.CASCADE)
    remote_addr = models.GenericIPAddressField(blank=True, null=True)
    ua = models.CharField(max_length=200, blank=True)
    data = models.TextField(blank=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "{}-{}".format(self.service.name, self.id)
