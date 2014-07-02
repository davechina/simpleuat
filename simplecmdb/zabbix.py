#!/usr/bin/env python2.7
# -*- coding:utf-8 -*-
# 2014-04-29 by liqinshan


import json
import urllib2


class ZabbixOperation(object):
	def __init__(self, url, user, passwd):
		self.url = url
		self.user = user
		self.passwd = passwd

	def get_data(self, data):
		req = urllib2.Request(self.url, data)
		req.add_header('Content-Type', 'application/json')

		try:
			response = urllib2.urlopen(req)
			result = json.loads(response.read())
			response.close()
			return result
		except URLError, e:
			if hasattr(e, 'reason'):
				print e.reason
			elif hasattr(e, 'code'):
				print e.code, e.read()


	def get_authid(self):
		data = json.dumps({
			'jsonrpc': '2.0',
			'method': 'user.login',
			'params': {
				'user': self.user,
				'password': self.passwd
				},
			'id': 0
			})

		response = self.get_data(data)
		authID = response.get('result')
		return authID


	def get_hostid(self, ip):
		data = json.dumps({
			'jsonrpc': '2.0',
			'method': 'host.get',
			'params': {
				'output': ['hostid', 'host', 'status'],
				'filter': {'host': ip}
				},
			'auth': self.get_authid(),
			'id': 1
			})

		response = self.get_data(data)
		res = response.get('result')
		if res:
			return res[0].get('hostid')
		else:
			return None


if __name__ == '__main__':
	zabbix_api = 'http://zabbixserver.qa.nt.ctripcorp.com/api_jsonrpc.php'
	zabbix_user = 'admin'
	zabbix_password = 'zabbix'

	zab = ZabbixOperation(zabbix_api, zabbix_user, zabbix_password)
	# print zab.get_hostid('192.168.82.56')
	# hostid = zab.get_hostid('SVR2084HP360')

	# if hostid:
	# 	grap_url = 'http://zabbixserver.uat.sh.ctriptravel.com/host_screen.php?hostid=%s&sid=8cb624a10c681eb8' % zab.get_hostid('SVR2084HP360')
	