# -*- coding: utf-8 -*-

from django.utils.safestring import mark_safe
import django_tables2 as tables
from models import *

def editable(field_name):
  return '{{% load inplace_edit %}}\n\n{{% inplace_edit "record.{field}" auto_height = 1 %}}'.format(field = field_name)

class TestTable(tables.Table):
    name = tables.TemplateColumn(editable('name'),verbose_name = "Наименование")
    prod_period = tables.TemplateColumn(editable('prod_period'),verbose_name = "Время производства")

    class Meta:
        model = Product
        attrs = {"class": "paleblue"}
