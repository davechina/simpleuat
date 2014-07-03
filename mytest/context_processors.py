# -*- coding:utf-8 -*-
from django.shortcuts import redirect

def auth_processor(req):
	if req.user.is_authenticated():
		return {'name': req.user.last_name}
	else:
		return {'name': req.user.username}