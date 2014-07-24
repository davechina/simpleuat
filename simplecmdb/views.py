# -*- coding:utf-8 -*-
from __future__ import absolute_import

from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required, permission_required
from django.views.decorators.csrf import csrf_exempt
from simplecmdb.models import Server, PD
from django.utils import simplejson
from django.core.exceptions import ObjectDoesNotExist
from .zabbix import ZabbixOperation
from .forms import AddServerForm
from django.db.models import Q
from .sql_zbx import GetZabbixData
from django.views.decorators.cache import cache_page
import datetime


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

@login_required(login_url='/login/')
def summary(req):
	servers = Server.objects.all()
	pds = PD.objects.all()

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

@csrf_exempt
def get_icmp_stat():
    user = r'uapp_zbxreader'
    password = r'wY4slvrnHcc7@tw'
    host = r'10.2.22.19'
    port = 55666
    db = 'zabbix'
    zbx = GetZabbixData(host, port, user, password, db)

    icmp_sql = r"select h.host,fn_getlastvalue(i.itemid,UNIX_TIMESTAMP()-delay-300) as value from items i inner join hosts h on i.hostid=h.hostid where key_ = 'icmpping';"
    icmp_stat = zbx.get_zbx_stat(icmp_sql)
    return dict(list(icmp_stat))

# @cache_page(60 * 60)
@csrf_exempt
def get_server_stat():
    user = r'uapp_zbxreader'
    password = r'wY4slvrnHcc7@tw'
    host = r'10.2.22.19'
    port = 55666
    db = 'zabbix'
    zbx = GetZabbixData(host, port, user, password, db)

    ser_sql = r"select host,max(if((key_= 'vm.memory.size[pavailable]'),value_avg,NULL)) AS vm,max(if((key_= 'system.swap.size[,pfree]'),value_avg,NULL)) AS swap,max(if((key_= 'system.cpu.load'),value_avg,NULL)) AS cpu from (select h.host,key_,avg(value) as value_avg from items i inner join hosts h on i.hostid=h.hostid inner join history his on i.itemid=his.itemid where key_ in ('vm.memory.size[pavailable]','system.swap.size[,pfree]','system.cpu.load') and clock>=UNIX_TIMESTAMP('%s') and clock<=UNIX_TIMESTAMP('%s') group by h.host,key_)tbl group by host;" % ((datetime.datetime.now()+datetime.timedelta(hours=-1)).strftime('%Y-%m-%d %H:00:00'), datetime.datetime.now().strftime('%Y-%m-%d %H:00:00'))
    ser_stat = zbx.get_zbx_stat(ser_sql)

    d = {}
    for i in ser_stat:
    	d.update({i[0]:{'mem_ava_per':i[1], 'swap_ava_per':i[2], 'cpu_load':i[3]}})
    return d


@login_required(login_url='/login/')
def servers(req):
	servers = Server.objects.all()
	pds = PD.objects.all()
	return render_to_response("servers.html", {'serverinfo': servers, 'pds': [(pd, pds.get(Name=pd).server_set.all().count) for pd in pds]}, context_instance=RequestContext(req))

@login_required(login_url='/login/')
def pd(req, pd_name):
	pds = PD.objects.all()
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


@login_required(login_url='/login')
def search(req):
	if req.method == "GET" and "getserver" in req.GET:
		servers = Server.objects.all()
		i_data = req.GET.get("getserver")
		o_data = servers.filter(Q(IPAddress__contains=i_data)| Q(HostName__contains=i_data)| Q(CPUInfo__contains=i_data)| Q(MemInfo__contains=i_data)| Q(OSInfo__contains=i_data)| Q(DiskTotal__contains=i_data)| Q(Role__contains=i_data)| Q(Comments__contains=i_data))

	return render_to_response("result.html",  {'serverinfo': o_data}, context_instance=RequestContext(req))


def help(req):
    return render_to_response("help.html")
