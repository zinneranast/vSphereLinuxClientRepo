from django.conf.urls import url
from vsphclient import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^index/$', views.index, name='index'),
    url(r'^login/$', views.login, name='login'),
    url(r'^logout/$', views.logout, name='logout'),
    url(r'^home/$', views.home, name='home'),
    url(r'^blocked/$', views.blocked, name='blocked'),
    url(r'^startmachine/$', views.startmachine, name='startmachine'),
    url(r'^stopmachine/$', views.stopmachine, name='stopmachine'),
    url(r'^suspendmachine/$', views.suspendmachine, name='suspendmachine'),
    url(r'^resetmachine/$', views.resetmachine, name='resetmachine'),
    url(r'^takesnapshot/$', views.takesnapshot, name='takesnapshot'),
    url(r'^revertsnapshot/$', views.revertsnapshot, name='revertsnapshot'),
    url(r'^managersnapshot/$', views.managersnapshot, name='managersnapshot'),
    url(r'^deploy/$', views.deploy, name='deploy'),
    url(r'^summary/$', views.summary, name='summary'),
    url(r'^switchmanager/$', views.switchmanager, name='switchmanager'),
    url(r'^addswitch/$', views.addswitch, name='addswitch'),
    url(r'^cpuuse/$', views.cpuuse, name='cpuuse'),
    url(r'^memoryuse/$', views.memoryuse, name='memoryuse'),
    url(r'^diskuse/$', views.diskuse, name='diskuse'),
    url(r'^networkuse/$', views.networkuse, name='networkuse'),
]
