# -*- coding:utf-8 -*-
from simplecmdb.models import AssetType, Project

# def auth_processor(req):
# 	if req.user.is_authenticated():
# 		return {'name': req.user.last_name}
# 	else:
# 		return {'name': req.user.username}


def sidebar_atypes(req):
    assettypes = AssetType.objects.select_related().all()
    return {'sidebar_atypes': assettypes}


def sidebar_pjs(req):
    pjs = Project.objects.select_related().all()
    return {'sidebar_apjs': pjs}
