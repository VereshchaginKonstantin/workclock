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
from . lightLogic import *

@periodic_task(run_every=crontab(minute='2, 32'))
def SetLightToLatestPeople():
	try:
		if IsWorkingDay():
			bot = telebot.TeleBot('475168535:AAGBZZCxRdoDvsqjk0nXOy1gprdQHgyuUmo') #prod
			helper = DataHelper()
			light = LightEngine()
			light.SetBot(bot) 
			light.SetLightsAndSendButton()
	except Exception as e:
		print(e)
		bot.send_message(213974204, str(e))

@periodic_task(run_every=crontab(minute='2', hour='12,18'))
def every_hour_sendEvents():
	try:
		bot = telebot.TeleBot('475168535:AAGBZZCxRdoDvsqjk0nXOy1gprdQHgyuUmo') #prod
		helper = DataHelper()
		report = Reports()
		report.SetBot(bot) 
		report.SendEvent()
	except Exception as e:
		print(e)
		bot.send_message(213974204, str(e))

@periodic_task(run_every=crontab(minute='0'))
def every_hour_sendLight():
	try:
		
		bot = telebot.TeleBot('475168535:AAGBZZCxRdoDvsqjk0nXOy1gprdQHgyuUmo') #prod
		helper = DataHelper()
		now = helper.GetNow()
		
		dweek = now.weekday() 
		bot.send_message(213974204, dweek)
		if now.hour == 9 and IsWorkingDay():		
			report = Reports()
			report.SetBot(bot) 
			report.SendLight()
	except Exception as e:
		print(e)
		bot.send_message(213974204, str(e))
	
@periodic_task(run_every=crontab(minute='0'))
def every_hour_SendLightPrivate():
	try:
		
		bot = telebot.TeleBot('475168535:AAGBZZCxRdoDvsqjk0nXOy1gprdQHgyuUmo') #prod
		helper = DataHelper()
		now = helper.GetNow()
		
		dweek = now.weekday()
		if now.hour == 8 and IsWorkingDay():		
			report = Reports()
			report.SetBot(bot) 
			report.SendLightPrivate()
	except Exception as e:
		print(e)
		bot.send_message(213974204, str(e))	

@periodic_task(run_every=crontab(minute='2'))
def every_hour_sendOverWork():
	try:
		helper = DataHelper()
		now = helper.GetNow()
		bot = telebot.TeleBot('475168535:AAGBZZCxRdoDvsqjk0nXOy1gprdQHgyuUmo') #prod
		
		if now.hour == 18: 
			report = Reports()
			report.SetBot(bot) 
			report.OverWorkingPrivate()
	except Exception as e:
		print(e)
		bot.send_message(213974204, str(e))
	 
@periodic_task(run_every=crontab(minute='0', hour='18', day_of_week='fri'))
def every_friday():
	try:
		bot = telebot.TeleBot('475168535:AAGBZZCxRdoDvsqjk0nXOy1gprdQHgyuUmo') #prod
		report = Reports()
		report.SetBot(bot) 
		report.WeeklyReport() 
	except Exception as e:
		print(e)
		bot.send_message(213974204, str(e))





