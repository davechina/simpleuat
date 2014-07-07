# -*- coding:utf-8 -*-
from django.db import models


class PD(models.Model):
	Name = models.CharField(primary_key=True, max_length=30)
	Contact = models.TextField(u'联络人', blank=True, null=True)

	def __unicode__(self):
		return self.Name


class Server(models.Model):
	IPAddress = models.CharField(u'IP', primary_key=True, max_length=20)
	HostName = models.CharField(u'主机名', max_length=20, blank=True, null=True)	
	OSInfo = models.CharField(u'操作系统', max_length=50, blank=True, null=True)
	CPUInfo = models.CharField(u'CPU核数', max_length=20, blank=True, null=True)
	MemInfo = models.CharField(u'内存大小', max_length=20, blank=True, null=True)
	DiskTotal = models.CharField(u'硬盘大小', max_length=20, blank=True, null=True)
	DiskInfo = models.TextField(u'分区信息', blank=True, null=True)
	Role = models.CharField(u'角色', max_length=20, blank=True, null=True)
	Comments = models.TextField(u'功能', blank=True, null=True)	
	Pd = models.ForeignKey(PD)

	def __unicode__(self):
		return self.IPAddress


