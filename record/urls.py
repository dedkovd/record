from django.conf.urls import patterns, include, url
from django.contrib.auth.views import login, logout

from django.contrib import admin
admin.autodiscover()

js_info_dict = {
    'packages': ('django.conf',),
}

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'record.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^product/$', 'asuzr.views.prod_list'),
    url(r'^product/(?P<prod_id>\d+)/$', 'asuzr.views.prod_detail'),
    url(r'^main/(?P<day>\d+)/(?P<month>\d+)/(?P<year>\d+)/$', 'asuzr.views.main', name='asuzr-main'),
    url(r'^orders/(?P<archive>\d+)/$', 'asuzr.views.orders',name='asuzr-orders'),
    url(r'^desreport/$', 'asuzr.views.desreport'),
    url(r'^production_table/(?P<order_id>\d+)/$', 'asuzr.views.production_table'),
    url(r'^sketches/(?P<order_id>\d+)/$', 'asuzr.views.sketches'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^inplaceeditform/', include('inplaceeditform.urls')),
    url(r'^accounts/login/$',  login),
    url(r'^accounts/logout/$', logout),
    url(r'^jsi18n$', 'django.views.i18n.javascript_catalog', js_info_dict),
)
