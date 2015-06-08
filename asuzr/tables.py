# -*- coding: utf-8 -*-

from django.utils.safestring import mark_safe
import django_tables2 as tables
from models import *

def editable(field_name):
  return '{{% load inplace_edit %}}\n\n{{% inplace_edit "record.{field}" auto_height = 1 %}}'.format(field = field_name)


class EditableColumn(tables.TemplateColumn):
  def __init__(self, field_name, *args, **kwargs):
    super(tables.TemplateColumn, self).__init__(*args, **kwargs)
    template = '{{% load inplace_edit %}}\n\n{{% inplace_edit "record.{field}" auto_height = 1 %}}'.format(field = field_name)
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

class SketchesTable(tables.Table):
  sketch_file = tables.FileColumn(verbose_name = 'Имя файла')
  sketch_image = tables.Column(verbose_name = 'Эскиз')

  class Meta:
    attrs = {'class': 'paleblue'}
