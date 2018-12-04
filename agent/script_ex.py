#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
云主机监控,采集主机信息:
1. 内存使用
2. 交换分区使用
3. 负载
4. cpu信息
5. 磁盘信息
6. 进程快照

尽可能的采集所需信息, 这样更全面的了解到主机健康状况,为后续分析主机提供数据.
"""

import datetime
import json
import os
import sys

import psutil


def get_memory():
    mem = psutil.virtual_memory()
    return {
        'total': mem.total,
        'available': mem.available,
        'percent': mem.percent
    }


def get_swap_memory():
    swap = psutil.swap_memory()
    return {
        'total': swap.total,
        'used': swap.used,
        'percent': swap.percent
    }


def get_loadavg():
    loadavgs = os.getloadavg()
    return {
        'avg1': float(loadavgs[0]),
        'avg5': float(loadavgs[1]),
        'avg15': float(loadavgs[2]),
    }


def get_cpu_info():
    return {
        'percent': psutil.cpu_percent(interval=0),
        'count': psutil.cpu_count()
    }


def get_disk_info():
    disk_info = []
    for part in psutil.disk_partitions(all=False):
        if os.name == 'nt':
            if 'cdrom' in part.opts or part.fstype == '':
                # skip cd-rom drives with no disk in it; they may raise
                # ENOENT, pop-up a Windows GUI error for a non-ready
                # partition or just hang.
                continue
        usage = psutil.disk_usage(part.mountpoint)
        disk_info.append({
            'device':  part.device,
            'total':  usage.total,
            'used': usage.used,
            'free': usage.free,
            'percent': usage.percent,
            'fstype': part.fstype,
            'mountpoint': part.mountpoint
        })
    return disk_info


def get_process_infos():
    procs = []
    for p in psutil.process_iter():
        try:
            p.dict = p.as_dict(['username', 'nice', 'memory_info',
                                'memory_percent', 'cpu_percent',
                                'cpu_times', 'name', 'cmdline', 'status'])
        except psutil.NoSuchProcess:
            pass
        else:
            procs.append(p)

    # return processes sorted by CPU percent usage
    procs = sorted(procs, key=lambda p: p.dict['memory_percent'],
                   reverse=True)

    process_infos = [

    ]
    for p in procs:
        # TIME+ column shows process CPU cumulative time and it
        # is expressed as: "mm:ss.ms"
        if p.dict['cpu_times'] is not None:
            ctime = datetime.timedelta(seconds=sum(p.dict['cpu_times']))
            ctime = "%s:%s.%s" % (ctime.seconds // 60 % 60,
                                  str((ctime.seconds % 60)).zfill(2),
                                  str(ctime.microseconds)[:2])
        else:
            ctime = ''
        if p.dict['memory_percent'] is not None:
            p.dict['memory_percent'] = round(p.dict['memory_percent'], 1)
        else:
            p.dict['memory_percent'] = ''
        if p.dict['cpu_percent'] is None:
            p.dict['cpu_percent'] = ''

        # (XXX:)为了减少数据,这里初步去掉没用数据.
        cmdline = " ".join(p.dict['cmdline']).strip()
        if not cmdline:
            continue
        process_infos.append({
            'pid': p.pid,
            'username': p.dict.get('username', ''),
            'nice': p.dict['nice'],
            'vms': getattr(p.dict['memory_info'], 'vms', 0),
            'rss': getattr(p.dict['memory_info'], 'rss', 0),
            'cpu_percent': p.dict['cpu_percent'],
            'memory_percent': p.dict['memory_percent'],
            'ctime': ctime,
            'name':  p.dict['name'],
            'cmdline': cmdline,
        })

    return process_infos


print(json.dumps({
    "memory": get_memory(),
    "swap": get_swap_memory(),
    "loadavg": get_loadavg(),
    "cpu": get_cpu_info(),
    "disk": get_disk_info(),
    "process": get_process_infos()
}))
