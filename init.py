# -*- encoding: utf-8 -*-


import os
import subprocess
import time
import traceback

ROOT_DIR = os.path.abspath(os.path.dirname(__file__))
UWSGI_CONFIG_FILE = os.path.join(ROOT_DIR, 'uwsgi.ini')

UWSGI_CONFIG_TEMPLATE = """
[uwsgi]
master=true
socket=127.0.0.1:8000
processes=4
socket-timeout=300
reload-mercy=10
vacuum=true
max-requests=1000
limit-as=1024
listen=128
buffer-size=30000
memory-report=true
home={virtualenv_dir}
chdir=/docker/heartbeats/src
module=heartbeats.wsgi:application
"""

SUPERVISOR_CONF = "/etc/supervisor/conf.d/supervisor-app.conf"

UWSGI_SUPERVISOR_TEMPLATE = """
[program:app-uwsgi]
command = {uwsgi_path} --ini {config}
stopsignal=QUIT
redirect_stderr=true
stderr_logfile_maxbytes=1MB
stdout_logfile=/var/log/uwsgi.log
stdout_logfile_maxbytes=1MB
user=root
"""

NGINX_SUPERVISOR_TEMPLATE = """
[program:nginx-app]
command = /usr/sbin/nginx  -g 'daemon off;'
"""

DJANGO_Q_TEMPLATE = """
[program:qcluster]
command={python} {project_dir}/manage.py {command}
directory=/
autostart=true
autorestart=false
stopasgroup=true
killasgroup=true
startretries=0
redirect_stderr=true
stderr_logfile_maxbytes=1MB
stdout_logfile=/var/log/qcluster.log
stdout_logfile_maxbytes=1MB
user=root
"""

CHECK_TEMPLATE = """
[program:check]
command={python} {project_dir}/manage.py check
directory=/
autostart=true
autorestart=false
stopasgroup=true
killasgroup=true
startretries=0
redirect_stderr=true
stderr_logfile_maxbytes=1MB
stdout_logfile=/var/log/check.log
stdout_logfile_maxbytes=1MB
user=root
"""


def get_python():
    out = subprocess.check_output('pipenv run which python', shell=True)
    return out.decode('utf-8').strip()


def get_uwsgi():
    out = subprocess.check_output('pipenv run which uwsgi', shell=True)
    return out.decode('utf-8').strip()


def update_django_res(python_path):
    cmds = [
        "{} src/manage.py makemigrations",
        "{} src/manage.py migrate",
        "{} src/manage.py collectstatic  --noinput"
    ]

    for cmd in cmds:
        out = subprocess.check_output(cmd.format(python_path), shell=True)
        print(out)


def update_uwsgi_config(python_path):
    """
    设置虚拟环境目录到uwsgi.ini,写入文件.
    """
    with open(UWSGI_CONFIG_FILE, "w") as f:
        f.write(
            UWSGI_CONFIG_TEMPLATE.format(
                virtualenv_dir=os.path.dirname(os.path.dirname(python_path))
            )
        )


def update_supervisor_config():
    """
    将uwsgi和nginx写入supervisor配置.
    """
    uwsgi_config = os.path.join(ROOT_DIR, 'uwsgi.ini')

    configs = [NGINX_SUPERVISOR_TEMPLATE]
    configs.append(UWSGI_SUPERVISOR_TEMPLATE.format(
        config=uwsgi_config,
        uwsgi_path=get_uwsgi()
    ))
    configs.append(DJANGO_Q_TEMPLATE.format(
        command='qcluster',
        python=get_python(),
        project_dir=os.path.join(ROOT_DIR, "src")
    ))
    configs.append(CHECK_TEMPLATE.format(
        python=get_python(),
        project_dir=os.path.join(ROOT_DIR, "src")
    ))


    with open(SUPERVISOR_CONF, "w") as f:
        f.write("\n\n".join(configs))


def main():
    os.chdir(ROOT_DIR)
    python_path = get_python()
    update_django_res(python_path)
    update_uwsgi_config(python_path)
    update_supervisor_config()


if __name__ == "__main__":
    main()
