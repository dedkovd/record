#!/usr/bin/env python 
# -*- coding: utf-8 -*- 

from django.db import models
from django.contrib.auth.models import User
from datetime import date, timedelta
from django.utils import dateformat
from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed
from django.db.models.signals import post_save, post_delete
from django.contrib.admin.models import LogEntry, ADDITION, CHANGE, DELETION
from django.contrib.contenttypes.models import ContentType
from django.dispatch import receiver
from gadjo.requestprovider.signals import get_request

#Изделия
class Product(models.Model):
  name = models.CharField(max_length=150)
  prod_period = models.IntegerField()#трудоемкость, дней

  def __unicode__(self):
    return self.name
  
#График работы  
class Schedule(models.Model):
  date = models.DateField()
  designer = models.ForeignKey(User)
  
  def __unicode__(self):
    return ' '.join((self.designer.first_name, self.designer.last_name))

#Таблица посещаемости
class Attendance(models.Model):
  date = models.DateField()
  calls = models.IntegerField()
  visits = models.IntegerField()
  
  @property
  def date_dd_mm_yy(self):
    return self.date.strftime("%d/%m/%Y")
  
  @property
  def date_as_tuple(self):
    return tuple(self.date_dd_mm_yy().split("/"))
  
  @property
  def order_count(self):
    return Order.objects.filter(date=self.date).count()
  
  @property
  def orders_price(self):
    orders = Order.objects.filter(date=self.date)
    day_price = sum(o.price for o in orders)
    return day_price
  
#Статьи затрат  
class CostItem(models.Model):
  name = models.CharField(max_length=150)
  default_item = models.BooleanField(default=False)
  
  def __unicode__(self):
   return self.name

#Заказы  
class Order(models.Model):
  date = models.DateField()						#дата
  product = models.ForeignKey(Product)					#id изделия
  price = models.DecimalField(max_digits=12, decimal_places=2)		#стоимость
  address = models.CharField(max_length=150)				#адрес
  designer = models.ForeignKey(User, related_name='+')			#id дизайнера
  deadline = models.DateField()						#срок сдачи
  delivery = models.BooleanField(default=False)				#доставка
  lifting = models.BooleanField(default=False)				#подъем
  paid = models.DecimalField(max_digits=12, decimal_places=2)		#оплачено
  approved = models.DateTimeField(null=True, blank = True)		#согласовано
  executor = models.ForeignKey(User, null = True, blank = True, related_name='+')	#id исполнителя
  is_done = models.BooleanField(default=False)				#сдан
  calls = models.TextField(null=True, blank = True)			#обзвон
  contact = models.CharField(max_length=150, null=True, blank = True)	#контактное лицо
  phone_num = models.CharField(max_length=150,null=True, blank = True)	#контактный телефон
  cancelled = models.BooleanField(default=False)			#отменен
  cost_items = models.ManyToManyField(CostItem, through='OrderCosts', related_name='+', null=True, blank=True)   #статьи затрат

  def __unicode__(self):
    return ', '.join((dateformat.format(self.date, 'd E Y'), self.product.name, self.address))
  
  @property
  def date_dmy(self):
    return self.date.strftime("%d/%m/%Y")
  
  @property
  def deadline_dmy(self):
    return self.deadline.strftime("%d/%m/%Y")
  
  @property
  def approved_date(self):
    return self.approved.strftime("%d/%m/%Y %H:%M")
  
  @property
  def sketch(self):
    return len(Sketch.objects.filter(order = self))

  @property
  def ostatok(self):
    return self.price-self.paid
  
  @property
  def calls_color(self):
    need_color=False
    if self.approved!=None:
      need_color = (date.today()-self.approved.date()>= timedelta(days = 10))
    need_color = need_color and (self.calls == '')
    
    return need_color
  
  def save(self, *args, **kwargs):
    super(Order, self).save(*args, **kwargs)
    cost_items = CostItem.objects.filter(default_item = True)
    for ci in cost_items:
      new_order_cost = OrderCosts(order = self, cost_item = ci, value = 0, formula = '')
      new_order_cost.save()
    
#Эскизы
class Sketch(models.Model):
  def get_sketch_path(self, file_name):
    template = 'sketches/%s'
    return template % '' if self.order == None else '%s/%s' % ((template % self.order.id), file_name)

  sketch_file = models.FileField(upload_to = get_sketch_path)	#путь к файу
  order = models.ForeignKey(Order)	#id заказа

  def __unicode__(self):
    return self.sketch_file.name

#Действия
class Action(models.Model):
  name = models.CharField(max_length=150)	#наименование действия
  
  def __unicode__(self):
   return self.name
  
#Производственный план
class ProdPlan(models.Model):
  start_date = models.DateField()	#дата начала
  end_date = models.DateField()		#дата окончания
  order = models.ForeignKey(Order)	#id заказа
  executor = models.ForeignKey(User)	#id исполнителя
  action = models.ForeignKey(Action)	#id действия
  
  def __unicode__(self):
   return ', '.join((str(self.start_date), self.order.product.name, self.action.name, self.executor.first_name))
  
#Протокол доступа
class AccessProtocol(models.Model):
  time = models.DateTimeField()				#время
  user = models.ForeignKey(User)			#id пользователя
  event = models.CharField(max_length=150)		#действие
  
#План заказов
class OrderPlan(models.Model):
  date = models.DateField()
  plan = models.DecimalField(max_digits=12, decimal_places=2)

  def __unicode__(self):
    return self.date.strftime('%B %Y')

# Затраты по заказам
class OrderCosts(models.Model):
  order = models.ForeignKey(Order, related_name='+')
  cost_item = models.ForeignKey(CostItem, related_name='+')
  value = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank = True)
  formula = models.CharField(max_length=150, null=True, blank = True)
  
  def __unicode__(self):
   return ', '.join((str(self.order.id), self.order.product.name, self.cost_item.name))


############################################################################################
# Signal handlers
############################################################################################

def auth_log(message, user = None):
  if user == None:
    user = User.objects.get(pk = 1)

  entry = LogEntry(user = user, object_repr = message, action_flag = 4)
  entry.save()

on_login = lambda **kwargs: auth_log(u'Вход в систему', kwargs['user'])
on_logout = lambda **kwargs: auth_log(u'Выход из системы', kwargs['user'])
on_login_error = lambda **kwargs: auth_log(u'Ошибка входа пользователя %s' % kwargs['credentials']['username']) 

user_logged_in.connect(on_login)
user_logged_out.connect(on_logout)
user_login_failed.connect(on_login_error)

def construct_log_entry(**kwargs):
    instance = kwargs['instance']
    content_type = ContentType.objects.get_for_model(instance)
    user = User.objects.get(username = get_request().META['USER'])
    log_entry = {}
    log_entry['user'] = user
    log_entry['object_repr'] = str(instance)
    log_entry['content_type'] = content_type 
    log_entry['object_id'] = instance.id
    return log_entry

#@receiver(post_save)
def after_save(*args, **kwargs):
    instance = kwargs['instance']
    if isinstance(instance, LogEntry): return
    log_entry = construct_log_entry(**kwargs)
    created = kwargs['created']
    log_entry['action_flag'] = ADDITION if created else CHANGE
    entry = LogEntry(**log_entry)
    entry.save()

#@receiver(post_delete)
def after_delete(*args, **kwargs):
    log_entry = construct_log_entry(**kwargs)
    log_entry['action_flag'] = DELETION
    entry = LogEntry(**log_entry)
    entry.save() 

@receiver(post_delete, sender=Sketch)
def sketch_delete(sender, instance, **kwargs):
    instance.sketch_file.delete(False)
