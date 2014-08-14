#!/usr/bin/env python2.7
# -*- coding:utf-8 -*-
# 2014-04-29 by dave.li
# updated 2014-08-05 by dave.li


import json
import urllib2


class ZabbixOperation(object):
	def __init__(self, url, user, passwd):
		self.url = url
		self.user = user
		self.passwd = passwd


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


	def get_data(self, data):
		req = urllib2.Request(self.url, data)
		req.add_header('Content-Type', 'application/json')

		try:
			response = urllib2.urlopen(req)
			result = json.loads(response.read())
			response.close()
			return result
		except urllib2.URLError, e:
			if hasattr(e, 'reason'):
				return e.reason
			elif hasattr(e, 'code'):
				return e.code, e.read()


	def get_templateid(self, *templatenames):
		"""
			template object:
			https://www.zabbix.com/documentation/2.0/manual/appendix/api/template/definitions
		"""
		self.templatenames = templatenames
		templates = [t for t in self.templatenames]

		data = json.dumps({
			    "jsonrpc": "2.0",
			    "method": "template.get",
			    "params": {
			        "output": "extend",
			        "filter": {
			            "host": templates
			        }
			    },
			    "auth": self.get_authid(),
			    "id": 1
			})

		response = self.get_data(data)
		res = response.get('result')

		if res:
			return [{'templateid': i.get('templateid')} for i in res]


	def get_hostid(self, ip):
		self.ip = ip
		data = json.dumps({
			'jsonrpc': '2.0',
			'method': 'host.get',
			'params': {
				'output': ['hostid', 'host', 'status'],
				'filter': {'host': self.ip}
				},
			'auth': self.get_authid(),
			'id': 1
			})

		response = self.get_data(data)
		res = response.get('result')

		if res:
			return res[0].get('hostid')


	def get_hostgroupid(self, groupname):
		self.groupname = groupname
		data = json.dumps({		
			    "jsonrpc": "2.0",
			    "method": "hostgroup.get",
			    "params": {
			        "output": "extend",
			        "filter": {
			            "name": [
			            	self.groupname
			            ]
			        }
			    },
			    "auth": self.get_authid(),
			    "id": 1
			})

		response = self.get_data(data)
		res = response.get('result')

		if res:
			return res[0].get('groupid')
		

	def create_host(self, host, ip, groupid, templateid):
		"""
			host interfaces object: 
			https://www.zabbix.com/documentation/2.0/manual/appendix/api/hostinterface/definitions#host_interface
		"""

		self.host = host
		self.ip = ip
		self.groupid = groupid
		self.templateid = templateid

		data = json.dumps({
				    "jsonrpc": "2.0",
				    "method": "host.create",
				    "params": {
				        "host": self.host,
				        "interfaces": [
				            {
				                "type": 1,
				                "main": 1,
				                "useip": 1,
				                "ip": self.ip,
				                "dns": "",
				                "port": "10050"
				            }
				        ],
				        "groups": [
				            {
				                "groupid": self.groupid
				            }
				        ],
				        "templates": self.templateid,
				        "inventory": {
				            "macaddress_a": "01234",
				            "macaddress_b": "56768"
				        }
				    },
				    "auth": self.get_authid(),
				    "id": 1
				})

		resp = self.get_data(data)
		return resp


# if __name__ == '__main__':
# 	zabbix_api = 'http://zabbixserver.qa.nt.ctripcorp.com/api_jsonrpc.php'
# 	zabbix_user = 'admin'
# 	zabbix_password = 'zabbix'

# 	zab = ZabbixOperation(zabbix_api, zabbix_user, zabbix_password)
	# print zab.get_hostid('192.168.82.56')
	# hostid = zab.get_hostid('SVR2084HP360')

	# if hostid:
	# 	grap_url = 'http://zabbixserver.uat.sh.ctriptravel.com/host_screen.php?hostid=%s&sid=8cb624a10c681eb8' % zab.get_hostid('SVR2084HP360')

	# groupid = zab.get_hostgroupid('uat-nt-windows')
	# templateid = zab.get_templateid('uat-Template OS Windows', 'Template App IIS WP', 'Template .NET CLR')
	# host = 'UAT0150'
	# ip = '10.2.24.74'
	# result = zab.create_host(host, ip, groupid, templateid)

	# if not result.get('result'):
	# 	err_message = 'Add server to zabbix failed. Error message: %s' % result.get('error').get('data')	
	# 	print err_message