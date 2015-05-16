from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'record.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^product/$', 'asuzr.views.prod_list'),
    url(r'^product/(?P<prod_id>\d+)/$', 'asuzr.views.prod_detail'),
    url(r'^main/(?P<day>\d+)/(?P<month>\d+)/(?P<year>\d+)/$', 'asuzr.views.main', name='asuzr-main'),
    url(r'^orders/(?P<archive>\d+)/$', 'asuzr.views.orders'),
    url(r'^desreport/$', 'asuzr.views.desreport'),
    url(r'^admin/', include(admin.site.urls)),
)
