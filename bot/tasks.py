# -*- coding: utf-8 -*-
from celery.decorators import task
import telebot
from celery.task.schedules import crontab
from celery.decorators import periodic_task
import json
import hashlib
import hmac
import requests
from time import sleep, time
from datetime import datetime, timedelta, date
from .models import *
import requests
from django.utils.translation import ugettext as _
from django.utils.translation import activate
import re
from django.db.models import Count, Min, Sum, Avg
from . groupLogic import *

@periodic_task(run_every=crontab(minute='7'))
def every_hour():
	try:
		now = timezone.now()
		bot = telebot.TeleBot('475168535:AAGBZZCxRdoDvsqjk0nXOy1gprdQHgyuUmo') #prod
		if now.hour > 18: 
			report = Reports()
			report.SetBot(bot) 
			report.OverWorking()
	except Exception as e:
		print(e)
		bot.send_message(213974204, str(e))
	 
@periodic_task(run_every=crontab(minute='0', hour='18', day_of_week='fri'))
def every_friday():
	try:
		
		bot = telebot.TeleBot('475168535:AAGBZZCxRdoDvsqjk0nXOy1gprdQHgyuUmo') #prod
		report = Reports()
		report.SetBot(bot) 
		report.reportWeeklyReport() 
	except Exception as e:
		print(e)
		bot.send_message(213974204, str(e))





