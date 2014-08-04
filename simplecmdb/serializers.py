# -*- coding:utf-8 -*-

from rest_framework import serializers
from simplecmdb.models import Server, PD

class ServerSerializer(serializers.Serializer):
	server = serializers.CharField(required=False, max_length=100)
	ip = serializers.CharField(required=True, max_length=100)
	os = serializers.CharField(required=False, max_length=100)
	cpu = serializers.CharField(required=False, max_length=100)
	memtotal = serializers.CharField(required=False, max_length=100)
	disktotal = serializers.CharField(required=False, max_length=100)
	role = serializers.CharField(required=False, max_length=100)
	pd = serializers.CharField(required=False, max_length=100)
	comments = serializers.CharField(required=False, max_length=100)
	icmp = serializers.CharField(required=False, max_length=100)
	cpu_average_load = serializers.CharField(required=False, max_length=100)
	mem_usage_percent = serializers.CharField(required=False, max_length=100)
	swap_usage_percent = serializers.CharField(required=False, max_length=100)

	def restore_object(self, attrs, instance=None):
		if instance:
			instance.server = attrs.get('server', instance.server)
			instance.ip = attrs.get('server', instance.server)
			instance.os = attrs.get('os', instance.os)
			instance.cpu = attrs.get('cpu', instance.cpu)
			instance.memtotal = attrs.get('memtotal', instance.memtotal)
			instance.disktotal = attrs.get('disktotal', instance.disktotal)
			instance.role = attrs.get('role', instance.role)
			instance.pd = attrs.get('pd', instance.pd)
			instance.comments = attrs.get('comments', instance.comments)
			instance.icmp = attrs.get('icmp', instance.icmp)
			instance.cpu_average_load = attrs.get('cpu_average_load', instance.cpu_average_load)
			instance.mem_usage_percent = attrs.get('mem_usage_percent', instance.mem_usage_percent)
			instance.swap_usage_percent = attrs.get('swap_usage_percent', instance.swap_usage_percent)

		return Server(**attrs)