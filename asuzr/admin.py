from django.contrib import admin
from asuzr.models import Product
from asuzr.models import Order
from asuzr.models import Sketch
from asuzr.models import Action
from asuzr.models import ProdPlan
from asuzr.models import AccessProtocol
from asuzr.models import OrderPlan
from asuzr.models import Attendance

# Register your models here.
#admin.site.register(Product)
class ProductAdmin(admin.ModelAdmin):
  list_display=('name', 'prod_period')
admin.site.register(Product, ProductAdmin)  
admin.site.register(Order)
admin.site.register(Sketch)
admin.site.register(Action)
admin.site.register(ProdPlan)
admin.site.register(AccessProtocol)
admin.site.register(OrderPlan)
class AttendAdmin(admin.ModelAdmin):
  list_display=('date', 'calls', 'visits')
admin.site.register(Attendance, AttendAdmin)