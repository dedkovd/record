# -*- coding: utf-8 -*-

from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext, Context, loader
from django.contrib.admin.models import LogEntry
from asuzr.models import *
from datetime import datetime, date, timedelta
from django.utils import dateformat
import calendar
from django.db.models import Count, Sum
from asuzr.common import *
from django.contrib.auth.decorators import login_required
from asuzr.tables import *
from asuzr.forms import *
from django_tables2 import RequestConfig

@login_required 
def prod_list(request):
  product_list = Product.objects.all()
  t = loader.get_template('asuzr/prod_list.html')
  c = Context({
    'product_list': product_list,
    })
  return HttpResponse(t.render(c))

@login_required 
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

def get_attendance_table(year, month, prefix):
  day_in_month = calendar.monthrange(year,month)[1]
  sdate = date(year,month,1)
  edate = date(year,month,day_in_month)

  month_days = {i+1: {'date': custom_date(year,month,i+1)} for i in range(day_in_month)}
  
  attend_list = Attendance.objects.filter(date__range = (sdate,edate))
  attend_sum = attend_list.aggregate(Sum('calls'), Sum('visits'))
  for attend in attend_list:
    month_days[attend.date.day]['attend'] = attend

  order_list = Order.objects.filter(date__range = (sdate,edate))
  order_sum = order_list.aggregate(Count('product'), Sum('price'))
  order_list = order_list.values('date')
  order_list = order_list.annotate(Count('product'), Sum('price'))

  for order in order_list:
    month_days[order['date'].day]['order'] = order

  schedule = Schedule.objects.filter(date__range = (sdate,edate))
  
  for designer in schedule:
    day = designer.date.day
    if 'designer' in month_days[day]:
      month_days[day]['designer'] = '%s, %s' % (month_days[day]['designer'], designer)
    else:
      month_days[day]['designer'] = designer

  month_plan = OrderPlan.objects.filter(date = sdate).first()
  month_plan = 0 if month_plan == None else month_plan.plan
  month_balance = month_plan - (order_sum['price__sum'] or 0)

  additional_info = {'title': 'Справочно', 
                     'rows': [
                              {'title': 'ПЛАН', 'value': month_plan},
                              {'title': 'Осталось до выполнения', 'value': month_balance},
                             ]
                    }

  table = VisitTable(month_days.values(), prefix = prefix)
  table.verbose_name = 'Сводная информация'
      
  table.set_summaries({
                        'calls': attend_sum['calls__sum'] or 0,
                        'visits': attend_sum['visits__sum'] or 0,
                        'orders': order_sum['product__count'] or 0,
                        'cost': order_sum['price__sum'] or 0,
                      })
 
  return table, additional_info

def get_day_orders_table(date, prefix):
  orders = Order.objects.filter(date = date)
  summaries = orders.aggregate(Sum('price'), Sum('paid'))
  table = DayOrdersTable(orders, prefix = prefix)
  table.verbose_name = u'Заказы на %s' % dateformat.format(date, 'd E Y')
  table.set_summary(summaries['price__sum'] or 0, summaries['paid__sum'] or 0)

  return table 

def create_attendance_if_need(date):
  attendance, created = Attendance.objects.get_or_create(date = date,
          defaults={'calls': 0, 'visits': 0})
  if created:
      attendance.save()

@log_view_call
@login_required
def visit_view(request):
  curr_date = datetime.strptime(request.GET.get('date', date.today().strftime('%d.%m.%Y')), '%d.%m.%Y')
  form = DateForm({'date':curr_date})
  create_attendance_if_need(curr_date)
  attendance_table, add_info = get_attendance_table(curr_date.year, curr_date.month, 'attendance-')
  RequestConfig(request, paginate={'per_page': 32}).configure(attendance_table)

  orders_table = get_day_orders_table(curr_date, 'orders-')
  RequestConfig(request).configure(orders_table)

  title = u'Таблица посещаемости на %s' % dateformat.format(curr_date, 'F Y')
  return render(request, 'asuzr/table2.html', {
                                               'table1': attendance_table, 
                                               'table2': orders_table,
                                               'additional_info': add_info,
                                               'title': title,
                                               'form': form})

@login_required 
def main(request, day, month, year):
  if day == None:
    day = str(date.today().day)
  if month == None:
    month = str(date.today().month)
  if year == None:
    year = str(date.today().year)
    
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

@log_view_call
@login_required
def sketches(request, order_id):
  curr_order = Order.objects.get(pk = order_id)
  if request.method == 'POST':
    if 'sketch_file' in request.FILES:
      files = request.FILES.getlist('sketch_file')
      for f in files:
        instance = Sketch(sketch_file = f, order = curr_order)
        instance.save()
      return redirect(sketches, order_id = order_id)

  table = SketchesTable(Sketch.objects.filter(order = curr_order))
  RequestConfig(request).configure(table)
  return render(request, 'asuzr/sketches.html', { 
                                                 'order_id': order_id, 
                                                 'table': table, 
                                                 'title': u'Эскизы заказа %s' % curr_order})

def delete_sketch(request):
  pk = request.GET.get('pk', -1)
  sketch = get_object_or_404(Sketch, pk = pk)
  order_id = sketch.order.pk
  sketch.delete()
  return redirect(sketches, order_id = order_id)

@log_view_call
@login_required 
def orders(request, archive):
  is_archive = (archive == '1')
  Table = ArchiveOrdersTable if is_archive else OrdersTable
  table = Table(Order.objects.filter(is_done = is_archive))
  title = u'Архивная таблица заказов' if is_archive else u'Таблица выхода заказов'
  RequestConfig(request).configure(table)
  return render(request, 'asuzr/table.html', {'table': table, 'title': title})

@log_view_call
@login_required 
def desreport(request):
  start_date = request.GET.get('sdate', date.today().strftime('%d.%m.%Y'))
  sdate = datetime.strptime(start_date, '%d.%m.%Y')
  end_date = request.GET.get('edate', date.today().strftime('%d.%m.%Y'))
  edate = datetime.strptime(end_date, '%d.%m.%Y')
  Table = DesignerTable
  table = Table(Order.objects.filter(cancelled=False, date__range=(sdate,edate)).values('designer__first_name','designer__last_name').annotate(Sum('price'),Count('designer')))
  title = u'Отчет по дизайнерам за '+' - '.join((start_date, end_date))
  form = DiapDateForm({'sdate': sdate, 'edate': edate})
  RequestConfig(request).configure(table)
  return render(request, 'asuzr/table.html', {'table': table, 'title': title, 'form': form})

@log_view_call
@login_required
def production_table(request, order_id):
  order_list = Order.objects.filter(is_done=False).order_by('-id')
  sel_order = Order.objects.filter(id=order_id)
  cost_items = sel_order.values('cost_items')
  t=loader.get_template('asuzr/order_costs.html')
  c=RequestContext(request,{
    'order_list' : order_list,
    'sel_order' : sel_order,
    'cost_items' : cost_items,
    })
  return HttpResponse(t.render(c))

@log_view_call
@login_required
def prod_plan_view(request):
  curr_date = datetime.strptime(request.GET.get('date', date.today().strftime('%d.%m.%Y')), '%d.%m.%Y')
  y,m,d = curr_date.year, curr_date.month, curr_date.day
  wd = curr_date.weekday()
  sdate = curr_date - timedelta(days = wd)
  edate = curr_date + timedelta(days = 6-wd)
  
  days =  [sdate + timedelta(days=i) for i in range(0,7)]
  week_days = {i.weekday(): {'date': custom_date(i.year,i.month,i.day)} for i in days}
  prodplan_list = ProdPlan.objects.filter(start_date__range = (sdate,edate))
  
  for prodplan in prodplan_list:
    week_days[prodplan.start_date.weekday()]['prodplan'] = prodplan
  
  table = ProdPlanTable(week_days.values())
  title = u'Производственный план на %s - %s' % (sdate.strftime('%d.%m.%Y'), edate.strftime('%d.%m.%Y'))
  form = DateForm({'date':curr_date})
  RequestConfig(request).configure(table)
  return render(request, 'asuzr/table.html', {'table': table, 'title': title, 'form': form})

@login_required
def log_view(request):
  log = LogEntry.objects.all()
  table = LogTable(log)
  RequestConfig(request).configure(table)
  return render(request, 'asuzr/table.html', {'table': table, 'title': 'Журнал операций'})
