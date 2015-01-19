# -*- coding:utf-8 -*-

from django.db import models
from django.utils.encoding import smart_unicode


class Project(models.Model):
    name = models.CharField(primary_key=True, max_length=30)
    contact = models.TextField(u'联络人', blank=True, null=True)

    def __unicode__(self):
        return smart_unicode(self.name)
    

class IDC(models.Model):
    name = models.CharField(primary_key=True, max_length=30)
    
    def __unicode__(self):
        return smart_unicode(self.name)


class AssetType(models.Model):
    name = models.CharField(primary_key=True, max_length=30)
    #project = models.ForeignKey(Project)

    def __unicode__(self):
        return smart_unicode(self.name)


class AssetField(models.Model):
    assettype = models.ManyToManyField(AssetType)
    name = models.CharField(primary_key=True, max_length=100)

    def __unicode__(self):
        return smart_unicode(self.name)


class Asset(models.Model):
    name = models.CharField(primary_key=True, max_length=30)
    assettype = models.ForeignKey(AssetType)
    project = models.ManyToManyField(Project)
    idc = models.ForeignKey(IDC)

    def __unicode__(self):
        return smart_unicode(self.name)


class AssetFieldValue(models.Model):
    asset = models.ForeignKey(Asset)
    assetinfo = models.ForeignKey(AssetField)
    fieldvalue = models.CharField(max_length=100, null=True, blank=True)

    def __unicode__(self):
        return smart_unicode(self.fieldvalue)
