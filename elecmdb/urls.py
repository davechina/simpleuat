from django.conf.urls import patterns, include, url
from simplecmdb.api import *

from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns('',
   # Examples:
   # url(r'^$', 'elecmdb.views.home', name='home'),
   # url(r'^blog/', include('blog.urls')),

   url(r'^admin/', include(admin.site.urls)),
   )


# login and logout
urlpatterns += patterns('django.contrib.auth.views',
  url(r'^login/$', 'login', {'template_name': 'login.html'}),
  url(r'^logout/$', 'logout', {'template_name': 'login.html'}),
  )


# simplecmdb urls
urlpatterns += patterns('simplecmdb.views',
    url(r'^$', 'summary'),
    url(r'^help/', 'help'),
    url(r'^asset/(?P<assetTypeName>.+)/$', 'asset', name='asset'),
    url(r'^asset_search/$', 'asset_search', name='search'),
    url(r'^project/(?P<projectName>.+)/$', 'project', name='project'),
    )


# restframework api
urlpatterns += patterns('',
    url(r'^api/projects/$', ProjectList.as_view()),
    url(r'^api/idcs/$', IDCList.as_view()),
    url(r'^api/assets/$', AssetList.as_view()),
    url(r'^api/atps/$', AssetTypeList.as_view()),
    url(r'^api/fields/$', AssetFieldList.as_view()),
    url(r'^api/afv/$', AssetFieldValueList.as_view()),

    url(r'^api/projects/(?P<pj>\w+)/$', 'simplecmdb.api.project_details'),
    url(r'^api/idcs/(?P<idcname>\w+)/$', 'simplecmdb.api.idc_details'), 
    url(r'^api/atps/(?P<atpname>\w+)/$', 'simplecmdb.api.atp_details'), 
    #url(r'^api/assets/(?P<assetname>\w+)/$', 'simplecmdb.api.asset_details'), 
    
    )
