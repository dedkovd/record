# -*- coding: utf-8 -*-
from django import forms
from django.forms import ModelForm
from datetime import date
from django.contrib.admin.widgets import AdminDateWidget
from asuzr.models import Order

class DateForm (forms.Form):
  date = forms.DateField(widget = AdminDateWidget(format='%d.%m.%Y'), 
          label = u'Дата', 
          initial = date.today)
  
class DiapDateForm (forms.Form):
  sdate = forms.DateField(widget = AdminDateWidget(format='%d.%m.%Y'),
          label = u'С', initial = date.today)
  edate = forms.DateField(widget = AdminDateWidget(format='%d.%m.%Y'), 
          label = u'по', initial = date.today)

class OrderForm(ModelForm):
  class Meta:
    model = Order
    fields = ['product', 'price', 'paid', 'address', 'deadline', 'delivery', 'lifting']
  
