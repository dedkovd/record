from django.shortcuts import render
from django.http import HttpResponse
from django.template import Context, loader
from asuzr.models import Product
from asuzr.models import Attendance
from asuzr.models import Order
from asuzr.models import OrderPlan
from datetime import datetime, date
from django.db.models import Count, Sum

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
  attend_list = Attendance.objects.all().order_by('date')
  filtered_attend_list=get_filtered_list(attend_list, year, month)
  
  p_date = datetime.strptime(day+'/'+month+'/'+year, '%d/%m/%Y')
  order_list = Order.objects.filter(date=p_date).order_by('id')
  
  plan = OrderPlan.objects.all()
  filtered_plan = get_filtered_list(plan, year, month)
  
  sum_calls = sum(l.calls for l in filtered_attend_list)
  sum_visits = sum(l.visits for l in filtered_attend_list)
  sum_orders = sum(l.order_count for l in filtered_attend_list)
  sum_price = sum(l.orders_price for l in filtered_attend_list)
  
  sum_order_price = sum(l.price for l in order_list)
  plan_balance = filtered_plan[0].plan-sum_price
  
  d_date = p_date.strftime("%d/%m/%Y")
    
  t = loader.get_template('asuzr/attend_order.html')
  c = Context({
    'attend_list': filtered_attend_list,
    'order_list': order_list,
    'sum_calls': sum_calls,
    'sum_visits': sum_visits,
    'sum_orders': sum_orders,
    'sum_price': sum_price,
    'sum_order_price': sum_order_price,
    'plan': filtered_plan[0],
    'balance': plan_balance,
    'd_date': d_date,
    })
  return HttpResponse(t.render(c))

def orders (request, archive):
  if archive=='0':
    is_done_value=False
  else:
    is_done_value=True
  
  order_list = Order.objects.filter(is_done=is_done_value).order_by('-id')
  t=loader.get_template('asuzr/orders.html')
  c=Context({
    'order_list': order_list,
    'archive': is_done_value,
    })
  return HttpResponse(t.render(c))

def desreport(request):
  start_date = request.GET.get('sdate', date.today().strftime('%d.%m.%y'))
  sdate = datetime.strptime(start_date, '%d.%m.%y')
  end_date = request.GET.get('edate', date.today().strftime('%d.%m.%y'))
  edate = datetime.strptime(end_date, '%d.%m.%y')
  des_list = Order.objects.filter(cancelled=False, date__range=(sdate,edate)).values('designer__first_name').annotate(Sum('price'),Count('designer'))
  t=loader.get_template('asuzr/desreport.html')
  c=Context({
    'des_list' : des_list,
    'start_date' : start_date,
    'end_date' : end_date,
    })
  return HttpResponse(t.render(c))

  


