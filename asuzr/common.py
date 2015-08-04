# -*- coding: utf-8 -*- 
from datetime import date
from django.contrib.admin.models import LogEntry
from django.contrib.auth.models import User

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
 def is_weekend(self):
    return self.weekday() >= 5

def log_view_call(fn):
    '''
    Wrapper for views log
    '''
    def wrapper(*args, **kwargs):
        log_entry = {}
        request = args[0]
        log_entry['user'] = User.objects.get(username = request.META['USER'])
        log_entry['object_repr'] = fn.__name__
        log_entry['action_flag'] = 5
        entry = LogEntry(**log_entry)
        entry.save()
        return fn(*args, **kwargs)
    return wrapper
