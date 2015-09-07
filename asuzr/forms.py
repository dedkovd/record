# -*- coding: utf-8 -*-
from django import forms
from django.forms import ModelForm
from datetime import date
from django.contrib.admin.widgets import AdminDateWidget, FilteredSelectMultiple, RelatedFieldWidgetWrapper
from django.forms.extras.widgets import Select
from django.db.models.fields.related import ManyToOneRel
from asuzr.models import *
from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe
from django.forms import widgets
from django.conf import settings

class RelatedFieldWidgetCanAdd(widgets.Select):

    def __init__(self, related_model, related_url=None, *args, **kw):

        super(RelatedFieldWidgetCanAdd, self).__init__(*args, **kw)

        if not related_url:
            rel_to = related_model
            info = (rel_to._meta.app_label, rel_to._meta.object_name.lower())
            related_url = 'admin:%s_%s_add' % info

        # Be careful that here "reverse" is not allowed
        self.related_url = related_url

    def render(self, name, value, *args, **kwargs):
        self.related_url = reverse(self.related_url)
        output = [super(RelatedFieldWidgetCanAdd, self).render(name, value, *args, **kwargs)]
        output.append(u'<a href="%s" class="add-another" id="add_id_%s" onclick="return showAddAnotherPopup(this);"> ' % (self.related_url, name))
        output.append(u'<img src="%sadmin/img/icon_addlink.gif" width="10" height="10" alt="%s"/></a>' % (settings.STATIC_URL, ('Add Another')))                                                                                                                               
        return mark_safe(u''.join(output))

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
    fields = ['product', 'price', 'paid', 'address', 'designer', 'deadline', 'delivery', 'lifting']

  submit_text = "Добавить заказ"
  product = forms.ModelChoiceField(
				    required=False,
				    queryset = Product.objects.all(),
				    widget=RelatedFieldWidgetCanAdd(Product)
				    )
  designer = forms.ModelChoiceField(queryset = User.objects.filter(groups__name='designers'))


class ProdTableForm(ModelForm):
  class Meta:
    model = OrderCosts
    fields = ['cost_item', 'value']
    
  submit_text = "Добавить"
  cost_item = forms.ModelChoiceField(
				    required=False,
				    queryset = CostItem.objects.all(),
				    widget=RelatedFieldWidgetCanAdd(CostItem)
				    )

class ProdPlanForm(ModelForm):
  class Meta:
    model = ProdPlan
    fields = ['start_date', 'order', 'executor','action']
  
  submit_text = "Добавить"
  start_date = forms.DateField(widget = AdminDateWidget(format = '%d.%m.%Y'))