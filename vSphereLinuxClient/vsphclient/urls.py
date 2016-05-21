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
    url(r'^takesnapshot/$', views.takesnapshot, name='takesnapshot')
]
