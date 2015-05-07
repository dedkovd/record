from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'record.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^product/$', 'asuzr.views.prod_list'),
    url(r'^product/(?P<prod_id>\d+)/$', 'asuzr.views.prod_detail'),
    url(r'^attendance/(?P<year>\d+)/(?P<month>\d+)/$', 'asuzr.views.attend_table'),
    url(r'^main/(?P<day>\d+)/(?P<month>\d+)/(?P<year>\d+)/$', 'asuzr.views.main', name='asuzr-main'),
    url(r'^orders/(?P<year>\d+)/(?P<month>\d+)/(?P<day>\d+)/$', 'asuzr.views.orders_table'),
    url(r'^attend_order/(?P<year>\d+)/(?P<month>\d+)/$', 'asuzr.views.attend_order_table'),
    url(r'^admin/', include(admin.site.urls)),
)
