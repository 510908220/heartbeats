# -*- encoding: utf-8 -*-

from djmail.template_mail import InlineCSSTemplateMail
import requests
from django_q.tasks import async
from django.conf import settings


def send_djmail(to, service_name, tp, value, grace, msg):
    o = InlineCSSTemplateMail('alert')
    o.send(to, {
        'service_name': service_name,
        'tp': tp,
        'value': value,
        'grace': grace,
        'msg': msg
    })


def send_djmail_async(to, service_name, tp, value, grace, msg):
    # send this message right away
    async('app.tasks.send_djmail',
          to,
          service_name,
          tp,
          value,
          grace,
          msg
          )
