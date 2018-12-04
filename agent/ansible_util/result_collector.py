import time
from collections import defaultdict

from ansible.plugins.callback import CallbackBase


class CallbackModule(CallbackBase):
    """
    Reference: https://github.com/ansible/ansible/blob/v2.0.0.2-1/lib/ansible/plugins/callback/default.py
    """

    CALLBACK_VERSION = 2.0

    def __init__(self):
        super(CallbackModule, self).__init__()
        self.start_timestamp = time.time()
        self.run_time_sec = 0
        self.__result_list = defaultdict(lambda:
                                         {
                                             "ok": [],
                                             "unreachable": [],
                                             "skipped": [],
                                             "failed": []
                                         }
                                         )
        self.__summary = {}

    def v2_runner_on_failed(self, result, ignore_errors=False):
        self.__result_list[result._host.get_name()]["failed"].append(result._result)

    def v2_runner_on_ok(self, result):
        self.__result_list[result._host.get_name()]["ok"].append(result._result)

    def v2_runner_on_skipped(self, result):
        self.__result_list[result._host.get_name()]["skipped"].append(result._result)

    def v2_runner_on_unreachable(self, result):
        self.__result_list[result._host.get_name()]["unreachable"].append(result._result)

    def v2_playbook_on_stats(self, stats):
        self.run_time_sec = time.time() - self.start_timestamp
        hosts = sorted(stats.processed.keys())

        for h in hosts:
            t = stats.summarize(h)
            self.summary[h] = t

    @property
    def summary(self):
        return self.__summary

    @property
    def results(self):
        return self.__result_list
