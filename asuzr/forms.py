from django import forms
from datetime import date

class DateForm (forms.Form):
  date = forms.DateField(label = 'Date')
