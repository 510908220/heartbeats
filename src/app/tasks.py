

import requests
from django_q.tasks import async
from django.conf import settings


def send_mail_async(from_, to, title, msg):
    # send this message right away
    async('django.core.mail.send_mail',
          title,
          msg,
          from_,
          to)
