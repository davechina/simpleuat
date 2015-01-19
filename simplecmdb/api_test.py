#!/usr/bin/env python
# -*- coding:utf8 -*-

import requests
import json


def operation(method, url, data=None, headers=None):
    if not url.endswith('/'):
        url = url + '/'
    
    r = requests.request(method, url, data=data, headers=headers)
    return r
    
    #if r.headers.get('content-type') == 'application/json':
    #    return {'code': r.status_code, 'content': r.json()}
    #else:
    #    return {'code': r.status_code, 'content': r.text}
        

if __name__ == '__main__':
    api = 'http://localhost/api'
    headers = {'content-type': 'application/json'}
    
    
    # Get data
    #idc_url = api + '/idcs'
    #method = 'GET'
    #response = operation(method, idc_url)

    # post idcs
    #idc_url = api + '/idcs'
    #method = 'POST'
    #idcs = ['M5', '星光']
    #
    #for idc in idcs:
    #    data = json.dumps({'name': idc.decode('utf8')})
    #    resp = operation(method, idc_url, data=data, headers=headers)
    #    print resp.status_code

    # post atps
    #atp_url = api + '/atps'
    #method = 'POST'
    #atps = ['服务器', '交换机']
    #
    #for atp in atps:
    #    data = json.dumps({'name': atp.decode('utf8')})
    #    resp = operation(method, atp_url, data=data, headers=headers)
    #    print resp.status_code
        
    # post projects
    project_url = api + '/projects/'
    method = 'POST'
    projects = ['www', 'Napos']
    
    for pj in projects:
        data = json.dumps({'name': pj})
        resp = operation(method, project_url, data=data, headers=headers)
        print resp.status_code
    