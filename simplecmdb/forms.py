from __future__ import absolute_import

from django.forms import ModelForm
from .models import PD, Server

class AddServerForm(ModelForm):
	class Meta:
		model = Server
		fields = ('HostName', 'IPAddress', 'OSInfo', 'CPUInfo', 'MemInfo', 'DiskTotal', 'Role', 'Comments', 'Pd')
