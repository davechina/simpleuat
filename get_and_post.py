#!/usr/bin/env python2.7
# -*- coding:utf-8 -*-

import os
import platform
import socket
import psutil
#import multiprocessing
from ConfigParser import SafeConfigParser
from datetime import datetime
import urllib, urllib2
import json


confFile = {"Windows" : "c:\\tags.cfg", "Linux" : "/etc/tags.cfg"}

class GetServerInfo(object):
	def __init__(self):
		pass

	def get_osInfo(self):
		system = platform.system()
		if system == 'Linux':
			osRelease = '-'.join(platform.linux_distribution()[:2])
		else:
			osRelease = '-'.join(platform.platform().split('-')[:2])

		return {'system':system, 'release':osRelease}


	def get_ipAddr(self):
		s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		s.connect(('1.2.3.4', 60000))	#分配1024以上的端口，mac系统中分配1024以下的端口，会报错：error: [Errno 49] Can't assign requested address。
		return s.getsockname()[0]


	def get_cpuNumber(self):
		#return multiprocessing.cpu_count()
		return psutil.cpu_count()


	def get_memTotal(self):
		m = psutil.virtual_memory().total
		return m/1024/1024


	def get_diskInfo(self):
		diskinfo = {}
		partitions = {}
		disks = [(dp, psutil.disk_usage(dp.mountpoint)) for dp in psutil.disk_partitions()]
		total = 0

		if platform.system() == "Linux":
			for dp, du in disks:
				total += du.total
				partitions[dp.device] = dp.device, dp.mountpoint, int(du.total/1024/1024/1024), int(du.used/1024/1024/1024), du.percent
		else:
			for dp, du in disks:
				total += du.total
				partitions[dp.device.split(':')[0]] = dp.device, int(du.total/1024/1024/1024), int(du.used/1024/1024/1024), du.percent
		
		diskinfo['total'] = int(total/1024/1024/1024)
		diskinfo['info'] = partitions
		
		return diskinfo


	def get_tags(self):
		c = SafeConfigParser()
		system = platform.system()
		cf = confFile.get(system)

		if not os.path.exists(cf):
			return {'pd':'备机', 'role':None, 'comments':None}
		else:
			f = c.read(cf)
			if system == "Linux":
				pd = c.get('pd', 'pd')
				pd_contact = c.get('pd', 'pd_contact')
				role = c.get('tags', 'role')
				comments = c.get('tags', 'function')
			else:
				pd = c.get('pd', 'pd').decode("gbk").encode("utf-8")
				pd_contact = c.get('pd', 'pd_contact').decode("gbk").encode("utf-8")
				role = c.get('tags', 'role').decode("gbk").encode("utf-8")
				comments = c.get('tags', 'function').decode("gbk").encode("utf-8")

			return {'pd':pd, 'pd_contact':pd_contact, 'role':role, 'comments':comments}


def main():
	info = GetServerInfo()
	data = {
		'ip' : info.get_ipAddr(),
		'hostname' : platform.node(),
		'os' : info.get_osInfo(),
		'cpu' : info.get_cpuNumber(),
		'mem' : info.get_memTotal(),
		'disk': info.get_diskInfo(),
		'tags' : info.get_tags(),
	}

	uri = 'http://xxx:8080/collect/'
	headers = {'content-type': 'application/json'}
	req = urllib2.Request(uri, data=json.dumps(data, ensure_ascii=False), headers=headers)
	response = urllib2.urlopen(req)


if __name__ == '__main__':
	main()
