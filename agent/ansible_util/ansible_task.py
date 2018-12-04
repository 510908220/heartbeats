from collections import namedtuple

from ansible.executor.playbook_executor import PlaybookExecutor
from ansible.executor.task_queue_manager import TaskQueueManager
from ansible.inventory import Inventory
from ansible.parsing.dataloader import DataLoader
from ansible.playbook.play import Play
from ansible.vars import VariableManager

from . import result_collector


class AnsibleTask(object):

    def __init__(self, host_list, private_key_file, forks, extra_vars=None):
        self._summary = {}
        self._results = {}

        self.variable_manager = VariableManager()
        if extra_vars:
            self.variable_manager.extra_vars = extra_vars
        self.loader = DataLoader()
        self.inventory = Inventory(loader=self.loader,
                                   variable_manager=self.variable_manager,
                                   host_list=host_list)
        Options = namedtuple('Options',
                             ['listtags', 'listtasks', 'listhosts', 'syntax', 'connection', 'module_path', 'forks',
                              'remote_user', 'private_key_file', 'ssh_common_args', 'ssh_extra_args',
                              'sftp_extra_args', 'scp_extra_args', 'become', 'become_method', 'become_user',
                              'verbosity', 'check'])

        self.options = Options(listtags=False,
                               listtasks=False,
                               listhosts=False,
                               syntax=False,
                               connection='ssh',
                               module_path=None,
                               forks=forks, remote_user='root',
                               private_key_file=private_key_file,
                               ssh_common_args=None,
                               ssh_extra_args=None,
                               sftp_extra_args=None,
                               scp_extra_args=None,
                               become=False,
                               become_method=None,
                               become_user='root',
                               verbosity=None, check=False)

    @property
    def summary(self):
        return self._summary

    @property
    def results(self):
        return self._results


class AnsiblePlayTask(AnsibleTask):

    def __init__(self, host_list, playbook_path, private_key_file="/root/.ssh/id_rsa", forks=5, extra_vars=None):
        super(AnsiblePlayTask, self).__init__(host_list, private_key_file, forks, extra_vars)
        passwords = {}
        self.call_back = result_collector.CallbackModule()
        self.pbex = PlaybookExecutor(playbooks=[playbook_path],
                                     inventory=self.inventory,
                                     variable_manager=self.variable_manager,
                                     loader=self.loader,
                                     options=self.options,
                                     passwords=passwords)
        self.pbex._tqm._stdout_callback = self.call_back

    def run(self):
        result = self.pbex.run()

        self._summary = self.call_back.summary
        self._results = self.call_back.results
        return result


class AnsibleAdhcTask(AnsibleTask):

    def __init__(self, host_list, module_name, args, private_key_file="/root/.ssh/id_rsa", forks=5, extra_vars=None):
        super(AnsibleAdhcTask, self).__init__(host_list, private_key_file, forks, extra_vars)
        self.call_back = result_collector.CallbackModule()

        # create inventory and pass to var manager
        inventory = Inventory(loader=self.loader,
                              variable_manager=self.variable_manager,
                              host_list=host_list)
        self.variable_manager.set_inventory(inventory)

        # create play with tasks
        play_source = dict(
            name="Ansible Play",
            hosts='all',
            gather_facts='no',
            tasks=[dict(action=dict(module=module_name, args=args))]
        )
        self.play = Play().load(play_source, variable_manager=self.variable_manager, loader=self.loader)

    def run(self):
        # actually run it
        tqm = None
        try:
            tqm = TaskQueueManager(
                inventory=self.inventory,
                variable_manager=self.variable_manager,
                loader=self.loader,
                options=self.options,
                passwords=dict(),
            )
            tqm._stdout_callback = self.call_back
            result = tqm.run(self.play)
            self._summary = self.call_back.summary
            self._results = self.call_back.results
            return result
        finally:
            if tqm is not None:
                tqm.cleanup()
