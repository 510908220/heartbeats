# -*- encoding: utf-8 -*-

import requests
from django.conf import settings

from django_q.tasks import async
from djmail.template_mail import InlineCSSTemplateMail


def send_djmail(to, service_name, tp, value, grace, msg):
    o = InlineCSSTemplateMail('alert')
    o.send(to, {
        'service_name': service_name,
        'tp': tp,
        'value': value,
        'grace': grace,
        'msg': msg
    })


def notify(to, service_name, tp, value, grace, msg):
    '''
    通知函数. 暂时是邮件,后面可以加入微信等
    '''
    send_djmail(to, service_name, tp, value, grace, msg)


def notify_async(to, service_name, tp, value, grace, msg):
    # send this message right away
    async('app.tasks.notify',
          to,
          service_name,
          tp,
          value,
          grace,
          msg
          )
