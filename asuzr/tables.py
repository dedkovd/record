# -*- coding: utf-8 -*-

from django.utils.safestring import mark_safe
import django_tables2 as tables
from models import *

def editable(field_name):
  return '{{% load inplace_edit %}}\n\n{{% inplace_edit "record.{field}" auto_height = 1 %}}'.format(field = field_name)


class EditableColumn(tables.TemplateColumn):
  def __init__(self, field_name, *args, **kwargs):
    super(tables.TemplateColumn, self).__init__(*args, **kwargs)
    print kwargs
    template = '{{% load inplace_edit %}}\n\n{{% inplace_edit "record.{field}" auto_height = 1 %}}'.format(field = field_name)
    self.template_code = template

class ThumbnailColumn(tables.TemplateColumn):
  def __init__(self, field_name, *args, **kwargs):
    super(tables.TemplateColumn, self).__init__(*args, **kwargs)
    template = '{{% load thumbnail %}}\n\n{{% thumbnail record.{field} "100x100" as im %}}<img src="{{{{ im.url }}}}">{{% endthumbnail %}}'.format(field = field_name)
    self.template_code = template

class TestTable(tables.Table):
    name = EditableColumn('name', "Наименование")
    prod_period = EditableColumn('prod_period', "Время производства")

    class Meta:
        model = Product
        attrs = {"class": "paleblue"}

class OrdersTable(tables.Table):
  date = tables.DateColumn('d/m/Y', verbose_name = 'Дата')
  deadline = tables.DateColumn('d/m/Y/', verbose_name = 'Срок сдачи')
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
  id = tables.Column(visible = False)
  designer = tables.Column(visible = False)
  calls = tables.Column(visible = False)
  contact = tables.Column(visible = False)
  phone_num = tables.Column(visible = False)
  cancelled = tables.Column(visible = False)

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

class ArchiveOrdersTable(OrdersTable):
  calls = EditableColumn('calls', verbose_name = 'Обзвон')

  class Meta:
    attrs = {'class': 'paleblue'}
    
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
