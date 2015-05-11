#!/usr/bin/env python 
# -*- coding: utf-8 -*- 

from django.db import models
from django.contrib.auth.models import User
from datetime import date, timedelta

# Create your models here.
#Соответствие названий и номеров дней недели
class Common:
  day_names = ("Понедельник","Вторник","Среда","Четверг","Пятница","Суббота","Воскресенье")
  day_colors = ("FFFFFF","FFFFFF","FFFFFF","FFFFFF","FFFFFF","#FFE4E1", "#FFE4E1")
  
#Изделия
class Product(models.Model):
  name = models.CharField(max_length=150)
  prod_period = models.IntegerField()#трудоемкость, дней

  def __unicode__(self):
    return self.name
  
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
  def week_day(self):
    day_number = self.date.weekday()
    day_name = Common.day_names[day_number]
    return day_name
  
  @property
  def day_color(self):
    day_number = self.date.weekday()
    color = Common.day_colors[day_number]
    return color
  
  @property
  def order_count(self):
    return Order.objects.filter(date=self.date).count()
  
  @property
  def orders_price(self):
    orders = Order.objects.filter(date=self.date)
    day_price = sum(o.price for o in orders)
    return day_price
  

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
  executor = models.ForeignKey(User, related_name='+')			#id исполнителя
  is_done = models.BooleanField(default=False)				#сдан
  calls = models.TextField(null=True, blank = True)			#обзвон
  contact = models.CharField(max_length=150, null=True, blank = True)	#контактное лицо
  phone_num = models.CharField(max_length=150,null=True, blank = True)	#контактный телефон
  cancelled = models.BooleanField(default=False)			#отменен
  
  @property
  def date_dmy(self):
    return self.date.strftime("%d/%m/%Y")
  
  @property
  def deadline_dmy(self):
    return self.deadline.strftime("%d/%m/%Y")
  
  @property
  def approved_date(self):
    return self.approved.strftime("%d/%m/%Y")
  
  @property
  def ostatok(self):
    return self.price-self.paid
  
  @property
  def calls_color(self):
    need_color=False
    if self.approved!=None:
      need_color = (date.today()-self.approved.date()>= timedelta(days = 10))
    return need_color
  
#Эскизы
class Sketch(models.Model):
  sketch_file = models.FileField(upload_to = 'sketches')	#путь к файу
  order = models.ForeignKey(Order)	#id заказа

#Действия
class Action(models.Model):
  name = models.CharField(max_length=150)	#наименование действия
  
#Производственный план
class ProdPlan(models.Model):
  start_date = models.DateField()	#дата начала
  end_date = models.DateField()		#дата окончания
  order = models.ForeignKey(Order)	#id заказа
  executor = models.ForeignKey(User)	#id исполнителя
  action = models.ForeignKey(Action)	#id действия
  
#Протокол доступа
class AccessProtocol(models.Model):
  time = models.DateTimeField()				#время
  user = models.ForeignKey(User)			#id пользователя
  event = models.CharField(max_length=150)		#действие
  
#План заказов
class OrderPlan(models.Model):
  date = models.DateField()
  plan = models.IntegerField()

  def __unicode__(self):
    return self.date.strftime('%B %Y')
