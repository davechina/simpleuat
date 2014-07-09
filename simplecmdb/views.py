# -*- coding:utf-8 -*-
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required, permission_required
from django.views.decorators.csrf import csrf_exempt
from simplecmdb.models import Server, PD
from django.utils import simplejson
from django.core.exceptions import ObjectDoesNotExist
from zabbix import ZabbixOperation
from forms import AddServerForm
from django.db.models import Q


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
			ser = Server(HostName=host, IPAddress=ip,  CPUInfo=cpunum, MemInfo=memtotal, OSInfo=os.get('release'), DiskTotal=disk.get('total'), DiskInfo=simplejson.dumps(disk.get('info')), Role=tags.get('role'), Comments=tags.get('comments'), Pd=PD.objects.get(Name=tags.get('pd')))
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

			ser = Server(HostName=data.get('HostName'), IPAddress=data.get('IPAddress'),  CPUInfo=data.get('CPUInfo'), MemInfo=data.get('MemInfo'), OSInfo=data.get('OSInfo'), DiskTotal=data.get('DiskTotal'), Role=data.get('Role'), Comments=data.get('Comments'), Pd=PD.objects.get(Name=data.get('Pd')))
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
