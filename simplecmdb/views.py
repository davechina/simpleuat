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
def get_server_and_pd():
	all_servers = Server.objects.all()
	all_pds = PD.objects.all()

	return {'all_servers': all_servers, 'all_pds': all_pds}


# @csrf_exempt
# def get_zbx_data(req):
# 	ser_stat = cache.get('ser_stat')
# 	if not ser_stat:
# 		ser_stat = sql_zbx.call_zbx('stat')
# 		cache.set('ser_stat', ser_stat, 3600)

# 	icmp_stat = cache.get('icmp_stat')
# 	if not icmp_stat:
# 		icmp_stat = sql_zbx.call_zbx('icmp')
# 		# cache.set('icmp_stat', icmp_stat, 300)
# 		cache.set('icmp_stat', icmp_stat, 3600)

# 	data = simplejson.loads(req.body)
# 	res = []

# 	for ser in data:
# 		ser = ser.strip()
# 		icmp = icmp_stat.get(ser)
# 		stat = ser_stat.get(ser)

# 		stat_ = {}
# 		if stat:
# 			stat_['icmp'] = icmp
# 			stat_['server'] = ser
# 			stat_['cpu_load'] = stat.get('cpu_load')
# 			stat_['mem_free_percent'] = stat.get('mem_ava_per')
# 			stat_['swap_free_percent'] = stat.get('swap_ava_per') 
# 		else:
# 			stat_['server'] = ser
# 			stat_['cpu_load'] = None
# 			stat_['mem_free_percent'] = None
# 			stat_['swap_free_percent'] = None
#			stat_['icmp'] = None			
# 		res.append(stat_)

# 	return HttpResponse(simplejson.dumps(res, ensure_ascii=False))


@csrf_exempt
def get_zbx_data():
	ser_stat = cache.get('ser_stat')
	if not ser_stat:
		ser_stat = sql_zbx.call_zbx('stat')
		cache.set('ser_stat', ser_stat, 3600)

	icmp_stat = cache.get('icmp_stat')
	if not icmp_stat:
		icmp_stat = sql_zbx.call_zbx('icmp')
		cache.set('icmp_stat', icmp_stat, 300)

	return {'ser_stat': ser_stat, 'icmp_stat':icmp_stat}


@login_required(login_url='/login/')
def summary(req):
	data = get_server_and_pd()
	servers = data.get('all_servers')
	pds = data.get('all_pds')

	try:
		avaliable = pds.get(Name="备机").server_set.all().count()
		avaliable_linux = pds.get(Name="备机").server_set.filter(OSInfo__contains="CentOS").count()
		avaliable_windows = pds.get(Name="备机").server_set.filter(OSInfo__contains="Windows").count()
	except ObjectDoesNotExist:
		avaliable = 0
		avaliable_linux = 0
		avaliable_windows = 0

	data = {
		'total':servers.count(),
		'windows': len(servers.filter(OSInfo__contains="Windows")),
		'linux': len(servers.filter(OSInfo__contains="CentOS")),
		# 'pds': pds,
		'pds': [(pd, pds.get(Name=pd).server_set.all().count) for pd in pds],
		'avaliable': avaliable,
		'avaliable_linux': avaliable_linux,
		'avaliable_windows': avaliable_windows,
	}

	return render_to_response("summary.html", data, context_instance=RequestContext(req))


@login_required(login_url='/login/')
def servers(req):
	data = get_server_and_pd()
	servers = data.get('all_servers')
	pds = data.get('all_pds')

	zbx_data = get_zbx_data()
	icmp_stat = zbx_data.get('icmp_stat')
	ser_stat = zbx_data.get('ser_stat')

	res = []
	for ser in servers:
		stat_ = {}

		icmp = icmp_stat.get(ser.HostName.upper())
		if not icmp:
			icmp = icmp_stat.get(ser.HostName.lower())

		stat = ser_stat.get(ser.HostName.upper())
		if not stat:
			stat = ser_stat.get(ser.HostName.lower())
		
		if not stat:
			stat_['cpu_average_load'], stat_['mem_usage_percent'], stat_['swap_usage_percent'] = None, None, None
		else:
			cpu_load = stat.get('cpu_load')
			if cpu_load:
				stat_['cpu_average_load'] = round(cpu_load, 2)
			else:
				stat_['cpu_average_load'] = None

			mem_free_percent = stat.get('mem_ava_per')
			if mem_free_percent:
				stat_['mem_usage_percent'] = str(round(100 - mem_free_percent, 2)) + '%'
			else:
				stat_['mem_usage_percent'] = None

			swap_free_percent = stat.get('swap_ava_per')
			if swap_free_percent:
				stat_['swap_usage_percent'] = str(round(100 - swap_free_percent, 2)) + '%'
			else:
				stat_['swap_usage_percent'] = None
			

		stat_['icmp'] = icmp
		stat_['server'] = ser.HostName.upper()
		stat_['ip'] = ser.IPAddress
		stat_['os'] = ser.OSInfo
		stat_['cpu'] = ser.CPUInfo
		stat_['memtotal'] = ser.MemInfo
		stat_['disktotal'] = ser.DiskTotal
		stat_['role'] = ser.Role
		stat_['pd'] = ser.Pd
		stat_['comments'] = ser.Comments				

		res.append(stat_)

	# return render_to_response("servers.html", {'serverinfo': servers, 'pds': [(pd, pds.get(Name=pd).server_set.all().count) for pd in pds]}, context_instance=RequestContext(req))
	return render_to_response("servers.html", {'res': res, 'pds': [(pd, pds.get(Name=pd).server_set.all().count) for pd in pds]}, context_instance=RequestContext(req))


@login_required(login_url='/login/')
def pd(req, pd_name):
	data = get_server_and_pd()
	pds = data.get('all_pds')

	try:
		pd_ser = pds.get(Name=pd_name).server_set.all()
		pd_contact = pds.get(Name=pd_name).Contact
	except:
		pd_ser = None
		pd_contact = None
	return render_to_response("pd.html", {'pd_ser': pd_ser, 'pd_name':pd_name, 'pd_contact':pd_contact, 'pds': [(pd, pds.get(Name=pd).server_set.all().count) for pd in pds]}, context_instance=RequestContext(req))	


@login_required(login_url='/login/')
def jump_zabbix(req, host):
	zabbix_api = 'http://zabbixserver.qa.nt.ctripcorp.com/api_jsonrpc.php'
	zabbix_user = 'admin'
	zabbix_password = 'zabbix'

	zab = ZabbixOperation(zabbix_api, zabbix_user, zabbix_password)
	hostid = zab.get_hostid(host)
	if hostid:
		grap_url = 'http://zabbixserver.qa.nt.ctripcorp.com/host_screen.php?hostid=%s&sid=40fa87ffa0252c78' % hostid
		return redirect(grap_url)
	else:
		# raise Http404
		return HttpResponse('No host found in zabbix server.')


@login_required(login_url='/login/')
def connect(req, ip):
    return render_to_response("connect.html", {'ip': ip})


@login_required(login_url='/login/')
@permission_required('simplecmdb.can_add_server')
def addserver(req):
	if req.method == "POST":
		form = AddServerForm(req.POST)
		if form.is_valid():
			data = form.cleaned_data

			ser = Server(HostName=data.get('HostName').strip(), IPAddress=data.get('IPAddress').strip(),  CPUInfo=data.get('CPUInfo'), MemInfo=data.get('MemInfo'), OSInfo=data.get('OSInfo'), DiskTotal=data.get('DiskTotal'), Role=data.get('Role'), Comments=data.get('Comments'), Pd=PD.objects.get(Name=data.get('Pd')))
			ser.save()
			return redirect('/')
	else:
		form = AddServerForm()

	return render_to_response("addserver.html", {'form': form}, context_instance=RequestContext(req))


@login_required(login_url='/login/')
def search(req):
	data = get_server_and_pd()
	servers = data.get('all_servers')

	if req.method == "GET" and "getserver" in req.GET:
		i_data = req.GET.get("getserver")
		o_data = servers.filter(Q(IPAddress__contains=i_data)| Q(HostName__contains=i_data)| Q(CPUInfo__contains=i_data)| Q(MemInfo__contains=i_data)| Q(OSInfo__contains=i_data)| Q(DiskTotal__contains=i_data)| Q(Role__contains=i_data)| Q(Comments__contains=i_data))

	return render_to_response("result.html",  {'serverinfo': o_data}, context_instance=RequestContext(req))


def help(req):
    return render_to_response("help.html")
