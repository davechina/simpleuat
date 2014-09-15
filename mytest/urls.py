from django.conf.urls import patterns, include, url
from django_cas.views import login, logout  
from django.views.decorators.csrf import csrf_exempt

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'mytest.views.home', name='home'),
    # url(r'^mytest/', include('mytest.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)


# simplecmdb
urlpatterns += patterns('simplecmdb.views',
    url(r'^collect/$', 'CollectHostInfo'),
    url(r'^$', 'summary'),
    url(r'^servers/$', 'servers'),
    url(r'^servers/(?P<host>[A-Za-z]+.+)/$', 'jump_zabbix', name='zabbix'),
    url(r'^servers/(?P<ip>\d+\.\d+\.\d+\.\d+)/$', 'connect', name='connect'),
    url(r'^pd/(?P<pd_name>.+)/$', 'pd', name="pd"),
    url(r'^help/$', 'help'),
    # url(r'^zbx/$', 'get_zbx_data'),
    url(r'^domain/$', 'domain'), 
    url(r'^server/$', 'server'), 
    url(r'^getRedis/$', 'get_redis'), 
    url(r'^charts/$', 'charts'), 
    )


# django_cas
urlpatterns += patterns('django_cas.views',
    url(r'^login/$', csrf_exempt(login)),
    url(r'^logout/$', logout),
    )


# rest_framework
urlpatterns += patterns('simplecmdb.views',
    url(r'api_server/$', 'servers_list'),
    url(r'api_server/(?P<host>\w+)$', 'server_detail'),
    )