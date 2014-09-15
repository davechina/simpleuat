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

		templates = [t for t in templatenames]

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


	def get_hostid(self, hostname):
		data = json.dumps({
			'jsonrpc': '2.0',
			'method': 'host.get',
			'params': {
				'output': ['hostid', 'host', 'status'],
				'filter': {'host': hostname}
				},
			'auth': self.get_authid(),
			'id': 1
			})

		response = self.get_data(data)
		res = response.get('result')

		if res:
			return res[0].get('hostid')


	def get_hostgroupid(self, groupname):
		data = json.dumps({		
			    "jsonrpc": "2.0",
			    "method": "hostgroup.get",
			    "params": {
			        "output": "extend",
			        "filter": {
			            "name": [
			            	groupname
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


	def get_proxyids(self):
		data = json.dumps({
		    "jsonrpc": "2.0",
		    "method": "proxy.get",
		    "params": {
		    	"output": "extend"
		    },
		    "auth": self.get_authid(),
		    "id": 1	
		})

		response = self.get_data(data)
		res = response.get('result')

		if res:
			return [{"proxy": i.get('host'), "proxyid" : i.get('proxyid')} for i in res]
	

	def get_hosts_monitored_by_proxy(self, proxyids):
		data = json.dumps({
		    "jsonrpc": "2.0",
		    "method": "proxy.get",
		    "params": {
		    	"proxyids": proxyids,
		    	"selectHosts": ["name", "hostid"]
		    },
		    "auth": self.get_authid(),
		    "id": 1			
			})

		response = self.get_data(data)
		res = response.get('result')

		if res:
			return res[0].get('hosts')


	def create_host(self, host, ip, groupid, templateid):
		"""
			host interfaces object: 
			https://www.zabbix.com/documentation/2.0/manual/appendix/api/hostinterface/definitions#host_interface
		"""

		data = json.dumps({
				    "jsonrpc": "2.0",
				    "method": "host.create",
				    "params": {
				        "host": host,
				        "interfaces": [
				            {
				                "type": 1,
				                "main": 1,
				                "useip": 1,
				                "ip": ip,
				                "dns": "",
				                "port": "10050"
				            }
				        ],
				        "groups": [
				            {
				                "groupid": groupid
				            }
				        ],
				        "templates": templateid,
				        "inventory": {
				            "macaddress_a": "01234",
				            "macaddress_b": "56768"
				        }
				    },
				    "auth": self.get_authid(),
				    "id": 1
				})

		resp= self.get_data(data)
		return resp


	def update_proxy(self, proxyid, hosts):
		data = json.dumps({
			    "jsonrpc": "2.0",
			    "method": "proxy.update",
			    "params": {
			        "proxyid": proxyid,
			        "hosts": hosts
			    },
			    "auth": self.get_authid(),
			    "id": 1
			})

		resp = self.get_data(data)
		return resp


if __name__ == '__main__':
	zabbix_api = 'http://zabbixserver.qa.nt.ctripcorp.com/api_jsonrpc.php'
	zabbix_user = 'admin'
	zabbix_password = 'zabbix'

	zab = ZabbixOperation(zabbix_api, zabbix_user, zabbix_password)