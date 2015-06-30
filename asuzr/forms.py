# -*- coding: utf-8 -*-
from django import forms
from datetime import date
from django.contrib.admin.widgets import AdminDateWidget

class DateForm (forms.Form):
  date = forms.DateField(widget = AdminDateWidget, label = u'Дата', initial = date.today)
  
class DiapDateForm (forms.Form):
  sdate = forms.DateField(widget = AdminDateWidget, label = u'С', initial = date.today)
  edate = forms.DateField(widget = AdminDateWidget, label = u'по', initial = date.today)
