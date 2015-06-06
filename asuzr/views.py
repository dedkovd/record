# -*- coding: utf-8 -*-

from django.shortcuts import render
from django.http import HttpResponse
from django.template import RequestContext, Context, loader
from asuzr.models import Product
from asuzr.models import Attendance
from asuzr.models import Order
from asuzr.models import OrderPlan
from asuzr.models import Schedule
from datetime import datetime, date, timedelta
import calendar
from django.db.models import Count, Sum
from asuzr.common import custom_date
from tables import *
from django_tables2 import RequestConfig

def prod_list(request):
  product_list = Product.objects.all()
  t = loader.get_template('asuzr/prod_list.html')
  c = Context({
    'product_list': product_list,
    })
  return HttpResponse(t.render(c))

def prod_detail(request, prod_id):
  return HttpResponse("This is %s" % prod_id)


def get_filtered_list(p_list, year, month):
  filtered_list=[]
  for a in p_list:
    a_date = a.date
    if a_date.strftime('%m/%Y').lstrip('0') == '/'.join((month,year)).lstrip('0'):
      filtered_list.append(a)
      
  return filtered_list

def get_orders_by_date(dt):
  order_list = Order.objects.filter(date=dt).order_by('id')
  return order_list


def main(request, day, month, year):
  d,m,y=int(day),int(month), int(year)
  
  attend_list = Attendance.objects.all().order_by('date')
  filtered_attend_list=get_filtered_list(attend_list, year, month)
  
  p_date = datetime.strptime(day+'/'+month+'/'+year, '%d/%m/%Y')
  order_list = Order.objects.filter(date=p_date).order_by('id')
  month_order_list=Order.objects.filter(date__range=(date(y,m,1),date(y,m,calendar.monthrange(y,m)[1]))).values('date').annotate(Count('product'),Sum('price'))
  
  plan = OrderPlan.objects.all()
  filtered_plan = get_filtered_list(plan, year, month)
  month_plan=0
  if len(filtered_plan) > 0:
    month_plan=filtered_plan[0].plan
    
  schedule = Schedule.objects.all().order_by('date')
  filtered_schedule = get_filtered_list(schedule, year, month)
  
  month_days={i: {'date': custom_date(int(year),int(month),i)}  for i in range(1,calendar.monthrange(int(year),int(month))[1]+1)}
  
  for l in filtered_attend_list:
    month_days[l.date.day]['attend']=l
    
  for s in filtered_schedule:
    if 'designers' in month_days[s.date.day]:
      des=', '.join((month_days[s.date.day]['designers'], ' '.join((s.designer.first_name, s.designer.last_name))))
      month_days[s.date.day]['designers'] = des
    else:
      month_days[s.date.day]['designers'] = ' '.join((s.designer.first_name, s.designer.last_name))
      
  for order in month_order_list:
    month_days[order['date'].day]['orders_count'] = order['product__count']
    month_days[order['date'].day]['orders_price'] = order['price__sum']

  month_days_values = month_days.values()
  
  sum_calls = sum(l.calls for l in filtered_attend_list)
  sum_visits = sum(l.visits for l in filtered_attend_list)
  sum_orders = sum(l['orders_count'] for l in month_days_values if 'orders_count' in l)
  sum_price = sum(l['orders_price'] for l in month_days_values if 'orders_price' in l)
  
  sum_order_price = sum(l.price for l in order_list)
  plan_balance = month_plan-sum_price
  
  d_date = p_date.strftime("%d/%m/%Y")
    
  t = loader.get_template('asuzr/attend_order.html')
  c = RequestContext(request,{
    'attend_list': month_days_values,
    'order_list': order_list,
    'sum_calls': sum_calls,
    'sum_visits': sum_visits,
    'sum_orders': sum_orders,
    'sum_price': sum_price,
    'sum_order_price': sum_order_price,
    'plan': month_plan,
    'balance': plan_balance,
    'd_date': d_date,
    })
  return HttpResponse(t.render(c))

def order_list(request):
  table = OrdersTable(Order.objects.filter(is_done=False))
  RequestConfig(request).configure(table)
  return render(request, 'asuzr/table.html', {'table': table, 'title': 'Таблица выхода заказов'})

def orders(request, archive):
  if archive=='0':
    return order_list(request)
  else:
    is_done_value=True
  
  o_list = Order.objects.filter(is_done=is_done_value).order_by('-id')
  t=loader.get_template('asuzr/orders.html')
  c=RequestContext(request, {
    'order_list': o_list,
    'archive': is_done_value,
    })
  return HttpResponse(t.render(c))

def desreport(request):
  start_date = request.GET.get('sdate', date.today().strftime('%d.%m.%y'))
  sdate = datetime.strptime(start_date, '%d.%m.%y')
  end_date = request.GET.get('edate', date.today().strftime('%d.%m.%y'))
  edate = datetime.strptime(end_date, '%d.%m.%y')
  des_list = Order.objects.filter(cancelled=False, date__range=(sdate,edate)).values('designer__first_name','designer__last_name').annotate(Sum('price'),Count('designer'))
  t=loader.get_template('asuzr/desreport.html')
  c=Context({
    'des_list' : des_list,
    'start_date' : start_date,
    'end_date' : end_date,
    })
  return HttpResponse(t.render(c))

def table_test(request):
  table = OrdersTable(Order.objects.filter(is_done=False))
  RequestConfig(request).configure(table)
  return render(request, 'asuzr/tabletest.html', {'table': table})
