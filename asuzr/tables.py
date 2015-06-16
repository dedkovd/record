# -*- coding: utf-8 -*-

from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe
from django.utils.html import escape
import django_tables2 as tables
from models import *

class EditableColumn(tables.TemplateColumn):
  def __init__(self, field_name, object_name = '', *args, **kwargs):
    super(tables.TemplateColumn, self).__init__(*args, **kwargs)
    template = '''
                {{{{% load inplace_edit %}}}}

                {main_part}
               '''
    main_part = ''
    if object_name == '':
       main_part = '''
                    {{% inplace_edit "record.{field}" auto_height = 1, auto_width = 1 %}}
                   '''
    else:
       main_part = '''
                    {{% if record.{object_name} %}}
                      {{% inplace_edit "record.{object_name}.{field}" auto_height = 1, auto_width = 1 %}}
                    {{% endif %}}
                   '''
    template = template.format(main_part = main_part)   
 
    self.template_code = template.format(field = field_name, object_name = object_name)

class ThumbnailColumn(tables.TemplateColumn):
  def __init__(self, field_name, *args, **kwargs):
    super(tables.TemplateColumn, self).__init__(*args, **kwargs)
    template = '''
                 {{% load thumbnail %}}

                 {{% thumbnail record.{field} "100x100" as im %}}
                   <img src="{{{{ im.url }}}}">
                 {{% endthumbnail %}}
               '''.format(field = field_name)
    self.template_code = template

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
  designer = tables.Column(visible = False) # Почему-то дизайнер в exclude вызывает ошибку, м.б. из-за FK. Разобраться

  def render_price(self, value):
    return '%0.1f' % value

  def render_ostatok(self, value):
    return '%0.1f' % value

  class Meta:
    model = Order
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
    exclude = ('id', 'calls', 'contact', 'phone_num', 'cancelled',)

class ArchiveOrdersTable(OrdersTable):
  calls = EditableColumn('calls', verbose_name = 'Обзвон')

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
    attrs = {'class': 'paleblue'}

class SketchesTable(tables.Table):
  sketch_file = tables.FileColumn(verbose_name = 'Имя файла')
  sketch_image = ThumbnailColumn('sketch_file', verbose_name = 'Эскиз', orderable = False)

  class Meta:
    attrs = {'class': 'paleblue'}

class VisitTable(tables.Table):
  date = tables.Column(verbose_name = 'Дата')
  week_day = tables.Column(verbose_name = 'День недели', accessor = 'date.weekday_name')
  calls = EditableColumn('calls', 'attend' ,verbose_name = 'Звонки', accessor = 'attend.calls')
  visits = EditableColumn('visits','attend', verbose_name = 'Посещения', accessor = 'attend.visits')
  orders = tables.Column(verbose_name = 'Заказы', accessor = 'order.product__count')
  cost = tables.Column(verbose_name = 'Стоимость', accessor = 'order.price__sum')
  designer = tables.Column(verbose_name = 'Дизайнеры')
 
  summary = ['Всего','',0,0,0,0,'']

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
  class Meta:
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
