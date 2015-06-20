# -*- coding: utf-8 -*-

from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe
from django.utils.html import escape
from django.contrib.admin.models import LogEntry
import django_tables2 as tables
from models import *

class EditableColumn(tables.TemplateColumn):
  def __init__(self, field_name, object_name = '', *args, **kwargs):
    template = '''
                {{{{% load inplace_edit %}}}}

                {main_part}
               '''
    main_part = ''
    params = 'auto_height = 1, auto_width = 1'
    if object_name == '':
       main_part = '''
                    {{% inplace_edit "record.{field}" {params} %}}
                   '''
    else:
       main_part = '''
                    {{% if record.{object_name} %}}
                      {{% inplace_edit "record.{object_name}.{field}" {params} %}}
                    {{% endif %}}
                   '''
    template = template.format(main_part = main_part)   
    template = template.format(field = field_name, object_name = object_name, params = params)

    super(EditableColumn, self).__init__(template, *args, **kwargs)

class ColoredEditableColumn(EditableColumn):
  def __init__(self, field_name, object_name = '', condition_field = None, *args, **kwargs):
    super(ColoredEditableColumn, self).__init__(field_name, object_name, *args, **kwargs)
    self.condition_field = condition_field

  def render(self, record, **kwargs):
    if self.condition_field != None and eval('record.%s' % self.condition_field):
      self.attrs = {'td': {'bgcolor': '#FFE4E1'}}
    else:
      self.attrs = {}
     
    return super(ColoredEditableColumn, self).render(record, **kwargs) 

class ThumbnailColumn(tables.TemplateColumn):
  def __init__(self, field_name, *args, **kwargs):
    template = '''
                 {{% load thumbnail %}}

                 {{% thumbnail record.{field} "100x100" as im %}}
                   <img src="{{{{ im.url }}}}">
                 {{% endthumbnail %}}
               '''.format(field = field_name)
    super(ThumbnailColumn, self).__init__(template, *args, **kwargs)

class OrdersTable(tables.Table):
  date = tables.DateColumn('d/m/Y', verbose_name = 'Дата')
  deadline = tables.DateColumn('d/m/Y', verbose_name = 'Срок сдачи')
  product = tables.Column(verbose_name = 'Наименование') 
  delivery = EditableColumn('delivery', verbose_name = 'Доставка')
  lifting = EditableColumn('lifting', verbose_name = 'Подъем')
  address = tables.Column(verbose_name = 'Адрес')
  price = tables.Column(verbose_name = 'Стоимость')
  paid = EditableColumn('paid', verbose_name = 'Оплачено')
  ostatok = tables.Column(verbose_name = 'Остаток')
  approved = EditableColumn('approved', verbose_name = 'Согласовано')
  sketch = tables.LinkColumn('asuzr.views.sketches', verbose_name = 'Эскизы', args=[tables.utils.A('pk')])
  executor = EditableColumn('executor', verbose_name = 'Исполнитель')
  is_done = EditableColumn('is_done', verbose_name = 'Сдан')

  def render_price(self, value):
    return '%0.2f' % value

  def render_ostatok(self, value):
    return '%0.2f' % value

  class Meta:
    model = Order
    empty_text = 'Незавершенных заказов нет'
    attrs = {'class': 'paleblue'}
    sequence = ('date', 
                'deadline', 
                'product', 
                'delivery', 
                'lifting', 
                'address',
                'price',
                'paid',
                'ostatok',
                'approved',
                'sketch',
                'executor',
                'is_done',)
    exclude = ('id', 'calls', 'contact', 'phone_num', 'cancelled', 'designer', )

class ArchiveOrdersTable(OrdersTable):
  calls = ColoredEditableColumn('calls', condition_field = 'calls_color', verbose_name = 'Обзвон')

  class Meta:
    attrs = {'class': 'paleblue'}
    empty_text = 'Архивных заказов нет'
    
class DesignerTable(tables.Table):
  full_name = tables.Column(empty_values=(), verbose_name = 'Дизайнер')
  designer__count = tables.Column(verbose_name = 'Всего заказов')
  price__sum = tables.Column(verbose_name = 'Общая сумма')
  
  def render_full_name(self, record):
    return " ".join((record['designer__first_name'], record['designer__last_name']))
  
  def render_sum_price(self, value):
    return '%0.1f' % value
  
  class Meta:
    empty_text = 'Заказов за этот период не было'
    attrs = {'class': 'paleblue'}

class SketchesTable(tables.Table):
  sketch_file = tables.FileColumn(verbose_name = 'Имя файла')
  sketch_image = ThumbnailColumn('sketch_file', verbose_name = 'Эскиз', orderable = False)
  delete_sketch = tables.Column(verbose_name = 'Удалить', orderable = False, empty_values = ())

  def render_delete_sketch(self, record):
    return mark_safe(u'<a href="%s?pk=%s">Удалить</a>' % 
                           (reverse('asuzr.views.delete_sketch'), escape(record.id)))

  class Meta:
    empty_text = 'Эскизов для этого заказа пока нет'
    attrs = {'class': 'paleblue'}

class VisitTable(tables.Table):
  date = tables.Column(verbose_name = 'Дата')
  week_day = tables.Column(verbose_name = 'День недели', accessor = 'date.weekday_name')
  calls = EditableColumn('calls', 'attend' ,verbose_name = 'Звонки', accessor = 'attend.calls')
  visits = EditableColumn('visits','attend', verbose_name = 'Посещения', accessor = 'attend.visits')
  orders = tables.Column(verbose_name = 'Заказы', accessor = 'order.product__count')
  cost = tables.Column(verbose_name = 'Стоимость', accessor = 'order.price__sum')
  designer = tables.Column(verbose_name = 'Дизайнеры')
 
  summary = ['Итого:','',0,0,0,0,'']

  def set_summaries(self, summaries):
   indexes = {'calls': 2, 'visits': 3, 'orders': 4, 'cost': 5}
   for s in summaries:
      idx = indexes[s]
      self.summary[idx] = summaries[s]
 
  def render_orders(self, value, record, column):
    value = 0 if value == None else value
    return mark_safe('<a href="%s?date=%s">%s</a>' % (
			reverse('asuzr.views.visit_view'), 
			record['date'].strftime('%d.%m.%Y'), 
			escape(value),
			))

  class Meta:
    attrs = {'class': 'paleblue'}
    orderable = False
    template = 'asuzr/weekend_table.html'

class DayOrdersTable(OrdersTable):
  designer = tables.Column(verbose_name = 'Дизайнер')

  summary = ['Итого:', 0, '', '', '',]

  def set_summary(self, price):
    self.summary[1] = price

  def render_designer(self, value):
    return ' '.join((value.first_name, value.last_name))

  class Meta:
    empty_text = 'Заказов для этого дня нет'
    attrs = {'class': 'paleblue'}
    exclude = ('date',
               'delivery', 
               'lifting', 
               'paid', 
               'ostatok', 
               'approved', 
               'sketch', 
               'executor', 
               'is_done',
              )
    sequence = ('product', 
                'price', 
                'address', 
                'designer', 
                'deadline',
               )
    template = 'asuzr/totals_table.html'
    
class ProdPlanTable(tables.Table):
  date = tables.Column(verbose_name = 'Дата')
  week_day = tables.Column(verbose_name = 'День недели', accessor = 'date.weekday_name')
  executor = EditableColumn('executor', 'prodplan',verbose_name = 'Исполнитель')
  order = EditableColumn('order', 'prodplan', verbose_name = 'Заказ')
  action = EditableColumn('action', 'prodplan', verbose_name = 'Действие')

  class Meta:
    attrs = {'class': 'paleblue'}

class LogTable(tables.Table):
  def render_action_flag(self, value):
    return {1: 'Добавление', 
            2: 'Изменение', 
            3: 'Удаление',
            4: 'Авторизация'}[value]

  class Meta:
    model = LogEntry
    attrs = {'class': 'paleblue'}
