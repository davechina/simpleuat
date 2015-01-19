# -*- coding:utf-8 -*-
from __future__ import absolute_import

from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ObjectDoesNotExist

from simplecmdb.models import *
from django.db.models import Q
import collections


@csrf_exempt
def summary(req):
    pjs = Project.objects.all()
    assets = Asset.objects.select_related().all()

    details = dict(collections.Counter([asset.assettype for asset in assets]))
    data = {
        "pjs": pjs,
        "assets": details
    }

    return render_to_response("summary.html", data, context_instance=RequestContext(req))


@csrf_exempt
def asset(req, assetTypeName):
    if req.method == "GET":
        tp = AssetType.objects.select_related().get(name=assetTypeName)
        assets = tp.asset_set.all()
        asset_fields = tp.assetfield_set.all()
        data = []

        if assets:
            for asset in assets:
                a_f_v = collections.OrderedDict()
                for asset_field in asset_fields:
                    try:
                        assetvalue = AssetFieldValue.objects.get(asset=asset, assetinfo=asset_field)
                    except ObjectDoesNotExist:
                        assetvalue = None
                    a_f_v['name'] = asset.name
                    a_f_v[asset_field] = assetvalue
                data.append(a_f_v)

            return render_to_response("asset.html", {'data': data, 'assettype': assetTypeName}, context_instance=RequestContext(req))
        else:
            return render_to_response("asset.html", {'data': data, 'assettype': assetTypeName}, context_instance=RequestContext(req))


@csrf_exempt
def asset_search(req):
    if req.method == "GET":
        req_param = req.GET.get("getasset").strip().encode('utf8')
        out = AssetFieldValue.objects.filter(
            Q(fieldvalue__icontains=req_param) |
            Q(assetinfo__name__icontains=req_param)
            )

        response_data = []
        if out:
            for i in out:
                asset = Asset.objects.get(name=i.asset.name)
                
                response_data.append({'assettype': asset.assettype.name, 'assetfield': i.assetinfo.name, 'assetfieldvalue': i.fieldvalue, 'assetproject': [pj.name.encode('utf8') for pj in asset.project.all()]})

            return render_to_response("result.html", {'resp': response_data}, context_instance=RequestContext(req))
        else:
            return render_to_response("result.html", {'resp': response_data}, context_instance=RequestContext(req))


@csrf_exempt
def project(req, projectName):
    if req.method == "GET":
        pj = Project.objects.select_related().get(name=projectName)
        atypes = {}.fromkeys([asset.assettype for asset in pj.asset_set.all()]).keys()
        data = []
        
        for tp in atypes:
            tpa = []
            for asset in tp.asset_set.all():
                a_f_v = collections.OrderedDict()
                for asset_field in tp.assetfield_set.all():
                    try:
                        assetvalue = AssetFieldValue.objects.get(asset=asset, assetinfo=asset_field)
                    except ObjectDoesNotExist:
                        assetvalue = None
                    a_f_v[tp] = tp
                    a_f_v['name'] = asset.name
                    a_f_v[asset_field] = assetvalue
                tpa.append(a_f_v)
            data.append(tpa)

        return render_to_response("project.html", {'data': data, 'projectName': projectName, 'contact': pj.contact}, context_instance=RequestContext(req))


@csrf_exempt
def help(req):
    return render_to_response("help.html", context_instance=RequestContext(req))

