# -*- coding:utf-8 -*-
from __future__ import absolute_import

from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from django.http import HttpResponse, Http404
from django.contrib.auth.decorators import login_required, permission_required
from django.views.decorators.csrf import csrf_exempt
from simplecmdb.models import Server, PD
from django.utils import simplejson
from django.core.exceptions import ObjectDoesNotExist
from .zabbix import ZabbixOperation
from .forms import AddServerForm
from django.db.models import Q
from django.core.cache import cache
from . import sql_zbx
import socket
import fnmatch
import random
import os

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from simplecmdb.serializers import ServerSerializer

import redis


@csrf_exempt
def CollectHostInfo(req):
	if req.method == 'POST':
		data = simplejson.loads(req.body)

		host = data.get('hostname')
		ip = data.get('ip')
		os = data.get('os')
		cpunum = data.get('cpu')
		memtotal = data.get('mem')
		disk = data.get('disk')
		tags = data.get('tags')

		pd = PD(Name=tags.get('pd'), Contact=tags.get('pd_contact'))
		pd.save()	
		
		if ip and host:
			ser = Server(HostName=host.strip(), IPAddress=ip.strip(),  CPUInfo=cpunum, MemInfo=memtotal, OSInfo=os.get('release'), DiskTotal=disk.get('total'), DiskInfo=simplejson.dumps(disk.get('info')), Role=tags.get('role'), Comments=tags.get('comments'), Pd=PD.objects.get(Name=tags.get('pd')))
			ser.save()	#如果model里没有设置primary_key，save()方法将默认执行insert动作。

	 	return HttpResponse('Information has been posted.')
	else:
	 	return HttpResponse('No data post.')


@csrf_exempt
def get_zbx_data():
	# icmp_stat = sql_zbx.call_zbx('icmp')
	# ser_stat = sql_zbx.call_zbx('stat')

	ser_stat = cache.get('ser_stat')
	if not ser_stat:
		ser_stat = sql_zbx.call_zbx('stat')
		cache.set('ser_stat', ser_stat, 3600)

	icmp_stat = cache.get('icmp_stat')
	if not icmp_stat:
		icmp_stat = sql_zbx.call_zbx('icmp')
		cache.set('icmp_stat', icmp_stat, 600)

	return {'ser_stat': ser_stat, 'icmp_stat':icmp_stat}


@csrf_exempt
def get_server_and_pd():
	all_ser = Server.objects.all()
	all_pds = PD.objects.all()

	zbx_data = get_zbx_data()
	icmp_stat = zbx_data.get('icmp_stat')
	ser_stat = zbx_data.get('ser_stat')

	res = []
	for ser in all_ser:
		hostname = ser.HostName
		stat_ = {}

		icmp = icmp_stat.get(hostname.upper())
		if not icmp:
			icmp = icmp_stat.get(hostname.lower())

		if not ser_stat.get(hostname.lower()) and not ser_stat.get(hostname.upper()):
			stat_['cpu_average_load'], stat_['mem_usage_percent'], stat_['swap_usage_percent'] = None, None, None

		else:
			stat = ser_stat.get(hostname.lower())
			if not stat:
				stat = ser_stat.get(hostname.upper())

			cpu_load = stat.get('cpu_load')
			if cpu_load:
				stat_['cpu_average_load'] = str(round(cpu_load, 2))

			mem_free_percent = stat.get('mem_ava_per')
			if mem_free_percent:
				stat_['mem_usage_percent'] = str(round(100 - mem_free_percent, 2)) + '%'

			swap_free_percent = stat.get('swap_ava_per')
			if swap_free_percent:
				stat_['swap_usage_percent'] = str(round(100 - swap_free_percent, 2)) + '%'

		stat_['icmp'] = icmp
		stat_['server'] = hostname.encode('utf8')
		stat_['ip'] = ser.IPAddress.encode('utf8')
		stat_['os'] = ser.OSInfo.encode('utf8')
		stat_['cpu'] = ser.CPUInfo.encode('utf8')
		stat_['memtotal'] = ser.MemInfo.encode('utf8')
		stat_['disktotal'] = ser.DiskTotal.encode('utf8')
		stat_['role'] = ser.Role.encode('utf8')
		stat_['pd'] = ser.Pd.Name.encode('utf8')
		stat_['comments'] = ser.Comments.encode('utf8')

		res.append(stat_)

	return {'all_servers': res, 'all_pds': all_pds}


@login_required(login_url='/login/')
def summary(req):
	data = get_server_and_pd()
	all_ser = data.get('all_servers')
	pds = data.get('all_pds')

	try:
		# avaliable = pds.get(Name="备机").server_set.all().count()
		# avaliable_linux = pds.get(Name="备机").server_set.filter(OSInfo__contains="CentOS").count()
		# avaliable_linux = pds.get(Name="备机").server_set.filter(OSInfo__contains="Windows").count()

		windows_count = len(filter(lambda x:'Windows' in x, [ser.get('os') for ser in all_ser]))
		linux_count = len(filter(lambda x:'CentOS' in x, [ser.get('os') for ser in all_ser]))
		avaliable_count = len(filter(lambda x:x=='备机', [ser.get('pd') for ser in all_ser]))
	except ObjectDoesNotExist:
		avaliable = 0
		avaliable_linux = 0
		avaliable_windows = 0

	data = {
		'total': len(all_ser),
		'windows_count': windows_count,
		'linux_count': linux_count,
		'avaliable_count': avaliable_count,
		'pds': [(pd, pds.get(Name=pd).server_set.all().count) for pd in pds]
	}

	return render_to_response("summary.html", data, context_instance=RequestContext(req))


@login_required(login_url='/login/')
def servers(req):
	data = get_server_and_pd()
	all_ser = data.get('all_servers')

	return render_to_response("servers.html", {'res': all_ser}, context_instance=RequestContext(req))


@login_required(login_url='/login/')
def pd(req, pd_name):
	data = get_server_and_pd()
	pds = data.get('all_pds')
	all_ser = data.get('all_servers')

	try:
		pd_contact = pds.get(Name=pd_name).Contact
		pd_ser = filter(lambda x : x.get('pd') == pd_name.encode('utf8'), all_ser)
	except:
		pd_contact = None
		pd_ser = None

	return render_to_response("pd.html", {'pd_ser': pd_ser, 'pd_name':pd_name, 'pd_contact':pd_contact}, context_instance=RequestContext(req))	


@login_required(login_url='/login/')
def jump_zabbix(req, host):
	zabbix_api = 'http://example.com/api_jsonrpc.php'
	zabbix_user = 'admin'
	zabbix_password = 'zabbix'

	zab = ZabbixOperation(zabbix_api, zabbix_user, zabbix_password)
	hostid = zab.get_hostid(host)
	if hostid:
		grap_url = 'http://example.com/host_screen.php?hostid=%s&sid=40fa87ffa0252c78' % hostid
		return redirect(grap_url)
	else:
		# raise Http404
		return HttpResponse('No host found in zabbix server.')


@login_required(login_url='/login/')
def connect(req, ip):
    return render_to_response("connect.html", {'ip': ip})


@login_required(login_url='/login/')
def server(req):
	if req.method == "GET" and "getserver" in req.GET:
		data = get_server_and_pd()
		all_ser = data.get('all_servers')
		o_data = []
		i_data = req.GET.get("getserver").strip().encode('utf8')

		for ser in all_ser:
			for v in ser.values():
				if v:
					if i_data.lower() in v or i_data.upper() in v:
						o_data.append(ser)
		return render_to_response("result.html",  {'serverinfo': o_data}, context_instance=RequestContext(req))

	elif req.method == 'POST':
		if req.user.has_perm('simplecmdb.can_add_server'):
			form = AddServerForm(req.POST)
			if form.is_valid():
				data = form.cleaned_data

				zabbix_api = 'http://example.com/api_jsonrpc.php'
				zabbix_user = 'admin'
				zabbix_password = 'zabbix'
				zab = ZabbixOperation(zabbix_api, zabbix_user, zabbix_password)

				host = data.get('HostName').strip()
				ip = data.get('IPAddress').strip()
				cpu = data.get('CPUInfo')
				mem = data.get('MemInfo')
				os = data.get('OSInfo')
				disk = data.get('DiskTotal')
				role = data.get('Role')
				comments = data.get('Comments')
				pd = PD.objects.get(Name=data.get('Pd'))

				ser = Server(HostName=host, IPAddress=ip,  CPUInfo=cpu, MemInfo=mem, OSInfo=os, DiskTotal=disk, Role=role, Comments=comments, Pd=pd)				
				ser.save()

				"""
				UAT zabbix group name:
					uat-nt-linux
					uat-nt-windows

				UAT zabbix template name:
					linux server template:
						uat-Template OS Linux

					windows server template:
						uat-Template OS Windows
						Template App IIS WP
						Template .NET CLR
				"""

				if 'Windows' in os:
					groupid = zab.get_hostgroupid('uat-nt-windows')
					templateid = zab.get_templateid('uat-Template OS Windows', 'Template App IIS WP', 'Template .NET CLR')
				elif 'CentOS' in os:
					groupid = zab.get_hostgroupid('uat-nt-linux')
					templateid = zab.get_templateid('uat-Template OS Linux')

				if groupid and templateid:
					result = zab.create_host(host, ip, groupid, templateid).get('result')

					if result:
						hostid = result.get('hostids')[0]
						proxy = random.choice([p.get("proxyid") for p in  zab.get_proxyids()])
						hosts = [i.get('hostid') for i in zab.get_hosts_monitored_by_proxy(proxy)]
						hosts.append(hostid)

						update_result = zab.update_proxy(proxy, hosts)

						if update_result:
							return redirect("/")
						else:
							message = 'Add host to proxy failed. Error message: %s' % result.get('error').get('data')
							render_to_response("addserver.html", {'message': message}, context_instance=RequestContext(req))
					else:
						message = 'Add host to zabbix failed. Error message: %s' % result.get('error').get('data')
						render_to_response("addserver.html", {'message': message}, context_instance=RequestContext(req))
				return redirect("/")

	elif req.method == 'GET':
		form = AddServerForm()
		return render_to_response("addserver.html", {'form': form}, context_instance=RequestContext(req))


def help(req):
    return render_to_response("help.html", context_instance=RequestContext(req))


@login_required(login_url='/login/')
def domain(req):
	data = get_server_and_pd()
	all_ser = data.get('all_servers')

	if req.method == "GET" and "getdomain" in req.GET:
		i_data = req.GET.get('getdomain').strip().encode('utf8')
		if i_data.startswith('http'):
			i_data = i_data.split('//')[1]
		o_data = socket.gethostbyname(i_data)

		if fnmatch.fnmatch(o_data, '10.2.29.*'):
			uat_webinfo = "http://example.com/Pool/List?Device=&Product=&Status=&Keyword=%s" % o_data
			return redirect(uat_webinfo)
		else:

			ser = filter(lambda x : x.get('ip') == o_data, all_ser)
			return render_to_response("result.html",  {'serverinfo': ser}, context_instance=RequestContext(req))


@api_view(['GET'])
def servers_list(req):
	if req.method == 'GET':
		data = get_server_and_pd()
		all_ser = data.get('all_servers')
		serializer = ServerSerializer(all_ser, many=True)
		return Response(serializer.data)


@api_view(['GET'])
def server_detail(req, host):
	data = get_server_and_pd()
	all_ser = data.get('all_servers')
	ser = filter(lambda x : x.get('server') == host.encode('utf8'), all_ser)

	if req.method == 'GET':
		serializer = ServerSerializer(ser)
		return Response(serializer.data)


def charts(req):
	return render_to_response("charts.html", context_instance=RequestContext(req))


def get_redis(req):
	def convert_value(data_, type_):
		for i in data_.keys():
			data_[i] = type_(data_[i])
		return data_

	r = redis.StrictRedis(host='10.2.20.210', port=6379)
	data = {}

	minionAlive = []
	keys = r.hkeys('minionAlive')[-10:]
	vals = map(lambda x: float(x)*100, r.hvals('minionAlive')[-10:])
	for i in zip(keys, vals):
		minionAlive.append(list(i))
	data['minionAlive'] = minionAlive

	data['minionNoresponse'] = r.hgetall('minionNoresponse')
	data['notaliveCount'] = convert_value(r.hgetall('notaliveCount'), int)
	data['aliveCount'] = convert_value(r.hgetall('aliveCount'), int)
	# data['minionAlive'] = convert_value(r.hgetall('minionAlive'), float)


	chart_data = simplejson.dumps(data)
	return HttpResponse(chart_data, mimetype="application/json")
