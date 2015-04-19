from django.shortcuts import render
from django.http import HttpResponse
from django.template import Context, loader
from asuzr.models import Product
from asuzr.models import Attendance
from asuzr.models import Order
from datetime import datetime, date, time
# Create your views here.

def prod_list(request):
  product_list = Product.objects.all()
  t = loader.get_template('asuzr/prod_list.html')
  c = Context({
    'product_list': product_list,
    })
  return HttpResponse(t.render(c))

def prod_detail(request, prod_id):
  return HttpResponse("This is %s" % prod_id)


def attend_table(request, year, month):
  attend_list = Attendance.objects.all().order_by('date')
  filtered_list=[]
  for a in attend_list:
    a_date = a.date
    if a_date.strftime('%m/%Y') == month+'/'+year:
      filtered_list.append(a)
      
  sum_calls = sum(l.calls for l in filtered_list)
  sum_visits = sum(l.visits for l in filtered_list)
  sum_orders = sum(l.order_count for l in filtered_list)
  sum_price = sum(l.orders_price for l in filtered_list)
  t = loader.get_template('asuzr/attendance.html')
  c = Context({
    'attend_list': filtered_list,
    'sum_calls': sum_calls,
    'sum_visits': sum_visits,
    'sum_orders': sum_orders,
    'sum_price': sum_price,
    })
  return HttpResponse(t.render(c))

def orders_table(request, year, month, day):
  p_date = datetime.strptime(day+'/'+month+'/'+year, '%d/%m/%Y')
  order_list = Order.objects.filter(date=p_date).order_by('id')
  sum_price = sum(l.price for l in order_list)
  t = loader.get_template('asuzr/orders.html')
  c = Context({
    'order_list': order_list,
    'sum_price': sum_price,
    })
  return HttpResponse(t.render(c))

def get_filtered_list(p_list, year, month):
  filtered_list=[]
  for a in p_list:
    a_date = a.date
    if a_date.strftime('%m/%Y') == month+'/'+year:
      filtered_list.append(a)
      
  return filtered_list

def get_orders_by_date(dt):
  order_list = Order.objects.filter(date=dt).order_by('id')
  return order_list

def attend_order_table(request, year, month):
  attend_list = Attendance.objects.all().order_by('date')
  filtered_attend_list=get_filtered_list(attend_list, year, month)
  
  order_list = Order.objects.all().order_by('id')
  filtered_order_list  = get_filtered_list(order_list, year, month)
  
  sum_calls = sum(l.calls for l in filtered_attend_list)
  sum_visits = sum(l.visits for l in filtered_attend_list)
  sum_orders = sum(l.order_count for l in filtered_attend_list)
  sum_price = sum(l.orders_price for l in filtered_attend_list)
  
  sum_order_price = sum(l.price for l in filtered_order_list)
    
  t = loader.get_template('asuzr/attend_order.html')
  c = Context({
    'attend_list': filtered_attend_list,
    'order_list': filtered_order_list,
    'sum_calls': sum_calls,
    'sum_visits': sum_visits,
    'sum_orders': sum_orders,
    'sum_price': sum_price,
    'sum_order_price': sum_order_price,
    })
  return HttpResponse(t.render(c))
  
  


