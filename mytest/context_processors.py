# -*- coding:utf-8 -*-
from django.shortcuts import redirect
from simplecmdb.models import PD

def auth_processor(req):
	if req.user.is_authenticated():
		return {'name': req.user.last_name}
	else:
		return {'name': req.user.username}

def sidebar_params(req):
	all_pds = PD.objects.all()

	return {'sidebar_all_pds': all_pds}
