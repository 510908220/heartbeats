# -*- encoding: utf-8 -*-

import json
import logging
import sys
import time

import pendulum
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from app.models import Service
from app.tasks import notify_async

logger = logging.getLogger("app")


class Command(BaseCommand):
    help = '服务健康检查'

    def notify(self, service, now):
        msg = '{service.name}({service.value},{service.grace}) not send heartbeat at {now}'.format(
            service=service,
            now=now.in_timezone(settings.TIME_ZONE).to_datetime_string()
        )
        logger.warning(msg)

        if not service.notify_to.strip():
            logger.warning('service %s notify_to is empty', service.name)
            return

        notify_async(service.notify_to.strip().split(";"),
                     service.name,
                     service.tp,
                     service.value,
                     service.grace,
                     msg
                     )

    def get_last_ping(self, service):
        latest_pings = service.pings.order_by('-id')[:1]
        if not latest_pings:
            return
        return latest_pings[0]

    def process_at_service(self, service):
        """
        当 当前时间 > at时,看[at, at + grace]之间是否有上报的数据
        """
        latest_ping = self.get_last_ping(service)
        if not latest_ping:
            return

        at = pendulum.parse(service.value, tz=settings.TIME_ZONE).in_timezone('UTC')
        last_created = pendulum.instance(latest_ping.created)
        now = pendulum.now(tz='UTC')

        if now < at.add(minutes=int(service.grace)):
            return
        if last_created < at:
            self.notify(service, now)

    def process_every_service(self, service):
        """
        当前时间距离上一次上报时间 > value + grace就告警
        """
        latest_ping = self.get_last_ping(service)
        if not latest_ping:
            return

        now = pendulum.now(tz='UTC')
        period = now - pendulum.instance(latest_ping.created)
        if period.total_minutes() > (int(service.value) + int(service.grace)):
            self.notify(service, now)

    def main(self):
        logger.info('start main')
        for service in Service.objects.all():
            logger.info("start check:%s,type:%s, value:%s, grace:%s, status:%s",
                        service.name,
                        service.tp,
                        service.value,
                        service.grace,
                        service.status
                        )
            if service.status == 'stoped':
                logger.warning('service %s is stoped', service.name)
                continue
            if service.tp == 'at':
                self.process_at_service(service)
            elif service.tp == 'every':
                self.process_every_service(service)

            logger.info('end check')
        logger.info('end main\n\n')

    def handle(self, *args, **options):
        while 1:
            try:
                self.main()
            except KeyboardInterrupt:
                logger.exception("KeyboardInterrupt")
                sys.exit(0)
            except Exception as e:
                logger.exception("Exception:%s", e)
            time.sleep(60 * 5)
