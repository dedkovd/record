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
  
  order_form = OrderForm(initial = {'designer': request.user})

  title = u'Таблица посещаемости на %s' % dateformat.format(curr_date, 'F Y')
  return render(request, 'asuzr/table2.html', {
                                               'table1': attendance_table, 
                                               'table2': orders_table,
                                               'additional_info': add_info,
                                               'title': title,
                                               'dateform': form,
                                               'add_form': order_form,
                                               'form_action': 'add-order'
                                               })


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

  sketch_list = Sketch.objects.filter(order = curr_order)
  return render(request, 'asuzr/sketches.html', { 
                                                 'order_id': order_id, 
                                                 'sketch_list': sketch_list, 
                                                 'title': u'Эскизы заказа %s' % curr_order})

def add_order(request):
  new_order = Order(date=date.today())
  form = OrderForm(request.POST, instance = new_order)
  form.save()
  return redirect(visit_view)

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
  return render(request, 'asuzr/table.html', {'table': table, 'title': title, 'dateform': form})

@log_view_call
@login_required
def production_table(request, order_id):
  order_costs = OrderCosts.objects.filter(order=order_id)
  table = ProductionTable(order_costs)
  curr_order = Order.objects.get(pk = order_id)
  title = u'Производственная таблица'  
  table.verbose_name  = u'Заказ: %s' % (', '.join((curr_order.product.name, curr_order.address)))
  table.verbose_name2 = u'Стоимость: %s' % str(curr_order.price)
  costs_sum = order_costs.aggregate(Sum('value'))
  table.set_summary(costs_sum['value__sum'] or 0)
  table.set_balance(curr_order.price - (costs_sum['value__sum'] or 0))
  
  form = ProdTableForm()
  
  RequestConfig(request).configure(table)
  return render(request, 'asuzr/table.html', 
		{'table': table, 'title': title, 'add_form': form, 'form_action': 'add-cost-items', 'params': order_id})

def production_table_add_item(request, order_id):
  curr_order = Order.objects.get(pk = order_id)
  new_item = OrderCosts(order=curr_order)
  form = ProdTableForm(request.POST, instance = new_item)
  form.save()
  return redirect(production_table, order_id = order_id)

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
  
  tables = []
  for week_day in week_days:
    tdate = week_days[week_day]['date']
    prodplan_list = ProdPlan.objects.filter(start_date = tdate)
    tables.append(ProdPlanTable(prodplan_list))
    tables[week_day].verbose_name = ', '.join((tdate.strftime('%d.%m.%Y'), tdate.weekday_name))
  
  title = u'Производственный план на %s - %s' % (sdate.strftime('%d.%m.%Y'), edate.strftime('%d.%m.%Y'))
  date_form = DateForm({'date':curr_date})
  add_form  = ProdPlanForm()
  for table in tables:
    RequestConfig(request).configure(table)
  return render(request, 'asuzr/table_n.html', {'tables': tables, 'title': title, 'dateform': date_form, 'add_form': add_form, 'form_action' : 'add-plan-item'})

def prod_plan_add_item(request):
  return redirect(prod_plan_view)

def create_plan_item_if_need(date):
  plan_item, created = ProdPlan.objects.get_or_create(start_date = date,
          defaults={'end_date': date})
  if created:
      plan_item.save()

@login_required
def log_view(request):
  log = LogEntry.objects.all()
  table = LogTable(log)
  RequestConfig(request).configure(table)
  return render(request, 'asuzr/table.html', {'table': table, 'title': 'Журнал операций'})
