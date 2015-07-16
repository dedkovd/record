# -*- coding: utf-8 -*- 
from datetime import date

class custom_date(date):

 day_names = ("Понедельник","Вторник","Среда","Четверг","Пятница","Суббота","Воскресенье")
 day_colors = ("FFFFFF","FFFFFF","FFFFFF","FFFFFF","FFFFFF","#FFE4E1", "#FFE4E1")
 
 @property
 def weekday_name(self):
    return self.day_names[self.weekday()]
 
 @property 
 def weekday_color(self):
    return self.day_colors[self.weekday()]
  
 @property
 def date_dd_mm_yy(self):
    return self.strftime('%d/%m/%Y')

 @property
 def is_weekend(self):
    return self.weekday() >= 5
