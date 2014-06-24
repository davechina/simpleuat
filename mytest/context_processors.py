# -*- coding:utf-8 -*-
from django.shortcuts import redirect

def auth_processor(req):
	if hasattr(req, 'user'):
		name = req.user.username
	else:
		from django.contrib.auth.models import AnonymousUser
		name = AnonymousUser()

	return {'name': name}