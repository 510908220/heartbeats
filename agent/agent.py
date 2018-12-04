# -*- encoding:utf-8 -*-

'''
监控agent模板
'''

import os
import sys
import json
import yaml
import requests
import logging
from logging.handlers import RotatingFileHandler


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

sys.path.append(os.path.join(BASE_DIR, 'ansible_util'))
from ansible_util import AnsiblePlayTask

CONFIG = {}


def init_log():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler = RotatingFileHandler(os.path.join(BASE_DIR, 'log', 'agent.log'),
                                       maxBytes=1024 * 1024 * 50,
                                       backupCount=10)
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.INFO)
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)
    return logger


class Agent(object):
    def __init__(self):
        self.config = self.__get_config()
        self.ip_infos = self.config['IPS']
        self.logger = init_log()
        self.report_server = 'http://{server_ip}/api/pings/?service={service}&&data='.format(
            server_ip=self.config['SERVER']['IP'],
            service=self.config['SERVER']['SERVICE'],

        )
        self.auth = (self.config['SERVER']['USER'], self.config['SERVER']['PASSWD'])

    def __get_config(self):
        config = {}
        with open(os.path.join(BASE_DIR, 'config.yaml')) as f:
            config = yaml.load(f.read())
        return config

    def send_heartbeat(self, error_msg=''):
        try:
            r = requests.post(self.report_server + error_msg, auth=self.auth)
        except Exception as e:
            self.logger.exception(e)

    def get_playbook(self):
        return os.path.join(BASE_DIR, 'playbook.yml')

    def get_extra_vars(self):
        return {
            'script': os.path.join(BASE_DIR, 'script.py')
        }

    def get_ok_result(self, ok_results):
        for ok_result in ok_results:
            if ok_result["invocation"]["module_name"] == "script":
                return ok_result["stdout"]

    def analyze(self, ip, result, is_ok=True):
        def has_process(p, processes):
            for process in processes:
                if p in process:
                    return True
            return False
        if not is_ok:
            return '{}:{}'.format(ip, result[:100])

        errors = []
        # 1. 读取配置里告警阀值
        ip_info = self.ip_infos[ip]
        mem_percent = ip_info['BASIC']['MEM']
        disk_percent = ip_info['BASIC']['DISK']
        cpu_percent = ip_info['BASIC']['CPU']
        process_list = ip_info['PROCESS']

        # 2. 根据获取机器最新数据和阀值对比
        machine_info = json.loads(result.strip())
        if machine_info['cpu']['percent'] > cpu_percent:
            errors.append('cpu:{}'.format(machine_info['cpu']['percent']))
        if machine_info['memory']['percent'] > mem_percent:
            errors.append('mem:{}'.format(machine_info['memory']['percent']))
        for disk_item in machine_info['disk']:
            if disk_item['percent'] > disk_percent:
                errors.append('{}:{}'.format(disk_item['device'], disk_item['percent']))
        for process in process_list:
            if not has_process(process, machine_info['process']):
                errors.append('process:{}'.format(process))

        # 3. 汇总结果
        if not errors:
            return
        return '{}:{}'.format(ip, ",".join(errors))

    def run_imp(self):
        play_task = AnsiblePlayTask(host_list=self.ip_infos.keys(),
                                    playbook_path=self.get_playbook(),
                                    private_key_file=self.config['AGENT']['SSH']['KEY'],
                                    extra_vars=self.get_extra_vars()
                                    )
        play_task.run()

        errors = []
        for ip, stat in play_task.summary.items():

            # 因为ok个数随着playbook里action的增加个数不一定,所以根据错误来判断是否成功
            if not sum((stat["unreachable"], stat["skipped"], stat["failures"])):
                result = self.get_ok_result(play_task.results[ip]["ok"])
                ret = self.analyze(ip, result)
            else:
                result = play_task.results[ip]
                ret = self.analyze(ip, result, False)
            if not ret:
                continue
            errors.append(ret)
        if not errors:
            self.send_heartbeat()
        else:
            self.logger.error(','.join(errors))
            self.send_heartbeat(','.join(errors))

    def run(self):
        self.logger.info('begin monitor')
        try:
            self.run_imp()
        except Exception as e:
            self.logger.exception(e)
        self.logger.info('end monitor')


if __name__ == '__main__':
    a = Agent()
    a.run()
