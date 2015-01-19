# -*- coding:utf-8 -*-

from rest_framework import serializers
from simplecmdb.models import *


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project


class IDCSerializer(serializers.ModelSerializer):
    class Meta:
        model = IDC


class AssetTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssetType


class AssetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Asset


class AssetFieldSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssetField


class AssetFieldValueSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssetFieldValue
