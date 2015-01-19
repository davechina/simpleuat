# -*- coding:utf-8 -*-

from simplecmdb.models import *
from simplecmdb.serializers import *
from django.core.exceptions import ObjectDoesNotExist

from rest_framework.generics import ListAPIView, ListCreateAPIView

from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view


class ProjectList(ListCreateAPIView):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    

class IDCList(ListCreateAPIView):
    queryset = IDC.objects.select_related().all()
    serializer_class = IDCSerializer


class AssetTypeList(ListCreateAPIView):
    queryset = AssetType.objects.select_related().all()
    serializer_class = AssetTypeSerializer


class AssetList(ListCreateAPIView):
    queryset = Asset.objects.select_related().all()
    serializer_class = AssetSerializer


class AssetFieldList(ListCreateAPIView):
    queryset = AssetField.objects.select_related().all()
    serializer_class = AssetFieldSerializer


class AssetFieldValueList(ListCreateAPIView):
    queryset = AssetFieldValue.objects.select_related().all()
    serializer_class = AssetFieldValueSerializer
    

@api_view(['GET', 'PUT', 'DELETE'])
def project_details(req, pj):
    try:
        pj = Project.objects.get(name=pj)
    except ObjectDoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if req.method == "GET":
        serializer = ProjectSerializer(pj)
        return Response(serializer.data)

    elif req.method == "PUT":
        serializer = ProjectSerializer(pj, data=req.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif req.method == "DELETE":
        pj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET', 'PUT', 'DELETE'])
def idc_details(req, idcname):
    try:
        idc = IDC.objects.get(name=idcname)
    except ObjectDoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    if req.method == "GET":
        serializer = IDCSerializer(idc)
        return Response(serializer.data)
    
    elif req.method == "PUT":
        serializer = IDCSerializer(idc, data=req.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif req.method == "DELETE":
        idc.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET', 'PUT', 'DELETE'])
def atp_details(req, atpname):
    try:
        atp = AssetType.objects.get(name=atpname)
    except ObjectDoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if req.method == "GET":
        serializer = AssetTypeSerializer(atp)
        return Response(serializer.data)

    elif req.method == "PUT":
        serializer = AssetTypeSerializer(atp, data=req.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif req.method == "DELETE":
        atp.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

