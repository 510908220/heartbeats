# -*- encoding: utf-8 -*-

import os
from collections import defaultdict
from pathlib import Path
import json
import subprocess
from django.conf import settings
from django.contrib.auth import get_user_model

from ansible_util import AnsiblePlayTask
from app.models import Asset, MonitorConfig, Alert


User = get_user_model()


class BaseMonitorExecutor(object):

    def __init__(self, username, category):
        self.category = category
        self.ansible_dir = Path(settings.BASE_DIR).joinpath('monitorx')
        self.username = username
        self.user = User.objects.get(username=username)
        self.monitorconfig = MonitorConfig.objects.get(owner=self.user, category=self.category)
        self.monitor_hosts = getattr(self.monitorconfig, '{0}_hosts'.format(self.category))

    def get_ok_result(self, ok_results):
        for ok_result in ok_results:
            if ok_result["invocation"]["module_name"] == "script":
                return ok_result["stdout"]

    def get_extra_vars(self):
        return {
            'script': str(self.ansible_dir.joinpath(self.category).joinpath('script.py'))
        }

    def get_playbook(self):
        return str(self.ansible_dir.joinpath(self.category).joinpath('playbook.yml'))

    def get_private_key_file(self):
        private_key_name = "{}_id_rsa".format(
            self.user.username
        )
        p = self.ansible_dir.joinpath(private_key_name)
        if p.exists():
            return str(p)

        with p.open('w') as f:
            f.write(self.user.authentications.get(category='private').data)

        subprocess.call(['chmod', '0600', str(p)])

        return str(p)

    def bad_result_process(self, host, result):
        Alert.objects.create(
            group=Asset.objects.get(ip=host.ip).group,
            owner=self.user,
            source=host.ip,
            level=Alert.LEVEL.danger,
            title='结果出错',
            content=str(result)
        )

    def analyze_result(self,  host, result):
        raise NotImplementedError("Subclasses should implement this!")

    def one_host_process(self, host, result):
        try:
            self.analyze_result(host, result)
        except:
            self.bad_result_process(host, result)

    def run(self):
        monitor_ips = [host.ip for host in self.monitor_hosts.all()]

        play_task = AnsiblePlayTask(host_list=monitor_ips,
                                    playbook_path=self.get_playbook(),
                                    private_key_file=self.get_private_key_file(),
                                    extra_vars=self.get_extra_vars()
                                    )
        play_task.run()

        # 不同处理逻辑

        for ip, stat in play_task.summary.items():
            host = self.monitor_hosts.get(ip=ip)
            # 因为ok个数随着playbook里action的增加个数不一定,所以根据错误来判断是否成功
            if not sum((stat["unreachable"], stat["skipped"], stat["failures"])):
                result = self.get_ok_result(play_task.results[ip]["ok"])
                self.one_host_process(host, result)
            else:
                self.bad_result_process(host, play_task.results[ip])


class NormalMonitorExecutor(object):

    def __init__(self, username, category, ips):
        self.ips = ips
        self.category = category
        self.ansible_dir = Path(settings.BASE_DIR).joinpath('ansible_toolbox')
        self.username = username
        self.user = User.objects.get(username=username)
        self.__success = {}
        self.__failure = {}

    def get_ok_result(self, ok_results):
        for ok_result in ok_results:
            if ok_result["invocation"]["module_name"] == "script":
                return ok_result["stdout"]

    def get_extra_vars(self):
        return {
            'script': str(self.ansible_dir.joinpath(self.category).joinpath('script.py'))
        }

    def get_playbook(self):
        return str(self.ansible_dir.joinpath(self.category).joinpath('playbook.yml'))

    def get_private_key_file(self):
        private_key_name = "{}_id_rsa".format(
            self.user.username
        )
        p = self.ansible_dir.joinpath(private_key_name)
        if p.exists():
            return str(p)

        with p.open('w') as f:
            f.write(self.user.authentications.get(category='private').data)

        subprocess.call(['chmod', '0600', str(p)])

        return str(p)

    def run(self):
        play_task = AnsiblePlayTask(host_list=self.ips,
                                    playbook_path=self.get_playbook(),
                                    private_key_file=self.get_private_key_file(),
                                    extra_vars=self.get_extra_vars()
                                    )
        play_task.run()

        for ip, stat in play_task.summary.items():
            # 因为ok个数随着playbook里action的增加个数不一定,所以根据错误来判断是否成功
            if not sum((stat["unreachable"], stat["skipped"], stat["failures"])):
                self.__success[ip] = self.get_ok_result(play_task.results[ip]["ok"])
            else:
                self.__failure[ip] = play_task.results[ip]

    @property
    def success(self):
        return self.__success

    @property
    def failure(self):
        return self.__failure
