from django.conf.urls import patterns, include, url
from django.contrib.auth.views import login, logout
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf import settings

from django.contrib import admin
admin.autodiscover()

js_info_dict = {
    'packages': ('django.contrib.admin',),
}

urlpatterns = patterns('',
    url(r'^product/$', 'asuzr.views.prod_list'),
    url(r'^product/(?P<prod_id>\d+)/$', 'asuzr.views.prod_detail'),
    url(r'^visits/$', 'asuzr.views.visit_view'),
    url(r'^order/add/$', 'asuzr.views.add_order', name = 'add-order'),
    url(r'^orders/(?P<archive>\d+)/$', 'asuzr.views.orders',name='asuzr-orders'),
    url(r'^desreport/$', 'asuzr.views.desreport'),
    url(r'^production_table/(?P<order_id>\d+)/$', 'asuzr.views.production_table'),
    url(r'^production_table/add_item/(?P<order_id>\d+)$', 'asuzr.views.production_table_add_item', name = 'add-cost-items'),
    url(r'^sketches/(?P<order_id>\d+)/$', 'asuzr.views.sketches'),
    url(r'^sketches/delete/$', 'asuzr.views.delete_sketch', name = 'asuzr-del-sketch'),
    url(r'^prodplan/$', 'asuzr.views.prod_plan_view'),
    url(r'^prodplan/add_item/$', 'asuzr.views.prod_plan_add_item', name = 'add-plan-item'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^log/$', 'asuzr.views.log_view'),
    url(r'^inplaceeditform/', include('inplaceeditform.urls')),
    url(r'^accounts/login/$',  login),
    url(r'^accounts/logout/$', logout),
    url(r'^jsi18n$', 'django.views.i18n.javascript_catalog', js_info_dict),
)

if settings.DEBUG:
    # static files (images, css, javascript, etc.)
    urlpatterns += patterns('',
        (r'^media/(?P<path>.*)$', 'django.views.static.serve', {
        'document_root': settings.MEDIA_ROOT})) 

