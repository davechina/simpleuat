# -*- coding:utf-8 -*-
from django.shortcuts import redirect

def auth_processor(req):
	if req.user.is_authenticated():
		name = req.user.last_name
		return {'name': name}
	else:
		return {'name': None}