# -*- coding: utf-8 -*-
 
from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import telebot
import json
from time import sleep, time
from datetime import datetime, timedelta, date
from . models import *
import random
import hashlib
import hmac
import requests
from math import floor
from django.contrib import messages
from django.db.models import F
from django.db.models import Q
import re
from django.utils.translation import ugettext as _
from django.utils.translation import activate
from django.db.models import Count, Min, Sum, Avg
from django.utils import timezone 
  
def IsUserBot(user):
	return user.GetDisplayName() == 'WorkingStatisticBot'

class ModelHelper:
	def Clear(self, user) :
		for workclock in WorkClock.objects.filter(user = user):
			workclock.delete()
		for journal in Journal.objects.filter(user = user):
			journal.delete()

	def GetWorkClock(self, user) :
		dateNow = timezone.now().date()
		if not WorkClock.objects.filter(user = user, day = dateNow).exists():
			workclock = WorkClock.objects.create(user = user, day = dateNow, is_enter = False)
		else:
			workclock = WorkClock.objects.filter(user = user, day = dateNow).first()
		return workclock
		
	def GetJournal(self, user) :
		dateNow = timezone.now().date()
		now = timezone.now()
		workclock = self.GetWorkClock(user)
		if not Journal.objects.filter(workclock = workclock).exists():
			journal = Journal.objects.create(workclock = workclock, user = user)
		else:
			journal = Journal.objects.filter(workclock = workclock).first()
		return journal

	def GetLightning(self, data, botEngine):
		user = self.GetUser(data, botEngine)
		if not Lightning.objects.filter(user = user).exists():
			Lightning.objects.create(user = user, count = 0)
		return Lightning.objects.filter(user = user).first()

	def GetGroup (self, data) :
		group_id = data['message']['chat']['id']
		group_name = data['message']['chat']['title']
		if not group.objects.filter(group_id = group_id).exists():
			group.objects.create(group_id=group_id, group_name = group_name)
		return group.objects.filter(group_id = group_id).first()
	def GetUser (self, data, botengine) :
		group = self.GetGroup(data)
		if 'new_chat_participant' in data['message']:
			user_id = data['message']['new_chat_participant']['id']
		elif 'left_chat_participant' in data['message']:
			user_id = data['message']['left_chat_participant']['id']
		elif 'from' in data['message']:
			user_id = data['message']['from']['id']
		#botengine.DebugMessage(group, "user_id, *%s*." % user_id)
		
		newusername = ''
		if 'new_chat_participant' in data['message']:
			if 'username' in data['message']['new_chat_participant']:
				newusername = data['message']['new_chat_participant']['username']
		elif 'from' in data['message']:
			if 'username' in data['message']['from']:
				newusername = data['message']['from']['username']
		elif 'left_chat_participant' in data['message']:
			if 'username' in data['left_chat_participant']['from']:
				newusername = data['message']['left_chat_participant']['username']
		#botengine.DebugMessage(group, "username, *%s*." % newusername)
		
		fio1 = ''
		if 'new_chat_participant' in data['message']:
			if 'first_name' in data['message']['new_chat_participant']:
				fio1 = data['message']['new_chat_participant']['first_name']
		elif 'from' in data['message']:
			if 'first_name' in data['message']['from']:
				fio1 = data['message']['from']['first_name']
		elif 'left_chat_participant' in data['message']:
			if 'first_name' in data['message']['left_chat_participant']:
				fio1 = data['message']['left_chat_participant']['first_name']
			
		#botengine.DebugMessage(group, "first_name, *%s*." % fio1)			
		
		fio2 = ''
		if 'new_chat_participant' in data['message']:
			if 'last_name' in data['message']['new_chat_participant']:
				fio2 = data['message']['new_chat_participant']['last_name']
		elif 'from' in data['message']:
			if 'last_name' in data['message']['from']:
				fio2 = data['message']['from']['last_name']
		elif 'left_chat_participant' in data['message']:	
			if 'last_name' in data['message']['left_chat_participant']:
				fio2 = data['message']['left_chat_participant']['last_name']
				
		#botengine.DebugMessage(group, "last_name, *%s*." % fio2)	
		
		fio = fio1 + " " + fio2		
		if not groupUser.objects.filter(user_id = user_id).filter(group = group).exists() :	
			guser = groupUser.objects.create(user_id=user_id, group = group, fio=fio.encode('utf8'), username=newusername, step="home")
		else:
			userToChange = groupUser.objects.filter(user_id = user_id).filter(group = group).first()
			if userToChange.fio != fio or userToChange.username != newusername:
				userToChange.fio = fio
				userToChange.username = newusername
				userToChange.save()
				
		return groupUser.objects.filter(user_id = user_id).filter(group = group).first()

class Reports:
	_botInternal = 0
	def SetBot(self,  botInside) :
		self._botInternal = botInside 
	
	def StatJournal(self, group, user, gfrom_message_id):
		dateNow = timezone.now().date()
		t = round(time())
		dweek = dateNow.weekday()
		d_start = dateNow - timedelta(days = dweek)
		mes = "*Подробная статистика для вас:*\n"
		#for journalEntry in Journal.objects.filter(user=user, date_in__gte = d_start, date_in__lte = dateNow):
		for journalEntry in Journal.objects.filter(user=user):
		#for journalEntry in Journal.objects.all():
			if not journalEntry.date_in is None:
				current_tz = timezone.get_current_timezone()
				local = current_tz.normalize(journalEntry.date_in.astimezone(current_tz))
				mes += "Пришел: {:%Y-%m-%d %H:%M}.".format(local) 
			if not journalEntry.date_out is None:
				local = current_tz.normalize(journalEntry.date_out.astimezone(current_tz))
				mes += " Ушел: {:%Y-%m-%d %H:%M}.\n".format(local)
			seconds = journalEntry.workclock.seconds
			if seconds is None:
				seconds = 0
			work_h = seconds // 3600
			work_m = (seconds - work_h*3600) // 60
			work_s = seconds - work_h*3600 - work_m*60
			mes += " Отработал: {} ч. {} мин. {} сек..\n".format(work_h, work_m, work_s)		
		self._botInternal.send_message(group.group_id, mes, parse_mode = "Markdown", reply_to_message_id = gfrom_message_id)
	
	def Stat(self, group):
		d = timezone.now().date()
		t = round(time())
		
		mes = "*Статистика за неделю:*\n"
		for guser in groupUser.objects.filter(group=group):
			dweek = d.weekday()
			d_start = d - timedelta(days = 6)
			seconds = WorkClock.objects.filter(user = guser, day__gte = d_start, day__lte = d).aggregate(Sum('seconds'))['seconds__sum']

			if seconds is None:
				seconds = 0
			work_h = seconds // 3600
			work_m = (seconds - work_h*3600) // 60
			work_s = seconds - work_h*3600 - work_m*60
			
			if not IsUserBot(guser):
				mes +=  "*{}*, работал: {} ч. {} мин. {} сек. ".format(guser.GetDisplayName(), work_h, work_m, work_s)
				lightcurr = Lightning.objects.filter(user = guser).first()
				if not lightcurr is None:
					count1 = lightcurr.count
				else:
					count1 = 0
				mes += "Молнии: *{}*.\n".format(count1)
					
		self._botInternal.send_message(group.group_id, mes, parse_mode = "Markdown")
	
	def OverWorking(self):
		d = timezone.now().date()  
		mes = "Пора домой: "
		
		for group1 in group.objects.all():		
			mes_ = ""
			for user in groupUser.objects.filter(group=group1):
				if  WorkClock.objects.filter(user = user, day=d, is_exit = False).exists():
					try:
						mes_ += "- {}\n".format(user.GetDisplayName()) 
						try:
							self._botInternal.send_message(user.user_id , "У вас пошла переработка, если вы не хотите отдыхать и полны сил, тогда все ок, если забыли написать в общий чат, что ушли, то сделайте это. Группа - {}".format(group1.group_name),  parse_mode = "Markdown")
							
						except:
							pass
					except Exception as e:
						print(e)
						self._botInternal.send_message(user.user_id, str(e))
			self._botInternal.send_message(group1.group_id, mes + mes_, parse_mode = "Markdown")			

	def WeeklyReport(self) :
		for group in group.objects.all():
			mes = "*Статистика за неделю:*\n"
			for guser in groupUser.objects.filter(group = group):
				d = timezone.now().date()
				dweek = d.weekday()
				d_start = d - timedelta(days = 6)
				seconds = WorkClock.objects.filter(user = guser, day__gte = d_start, day__lte = d).aggregate(Sum('seconds'))['seconds__sum']
				if seconds is None:
					seconds = 0
				work_h = seconds // 3600
				work_m = (seconds - work_h*3600) // 60
				work_s = seconds - work_h*3600 - work_m*60
  
				if not IsUserBot(guser):
					mes += "*{}*, работал: {} ч. {} мин. {} сек. ".format(guser.GetDisplayName(), work_h, work_m, work_s)
					lightcurr = Lightning.objects.filter(user = guser).first()
					if not lightcurr is None:
						count1 = lightcurr.count
					else:
						count1 = 0
				mes += "Молнии: %d.\n" % count1
			_botInternal.send_message(group.group_id, mes, parse_mode = "Markdown")
	
class BotEngineGroup:
	_botInternal = 0
	_modelHelper = 0
	def SetBot(self,  botInside) :
		self._botInternal = botInside
		self._modelHelper = ModelHelper()

	def Help(self, user) :
		self._botInternal.send_message(user.user_id, "/det - детальный план")
		self._botInternal.send_message(user.user_id, "/over - (по всем группам) рассылает всем сообщение о переработке, что бы вышли если в системе")
		self._botInternal.send_message(user.user_id, "/week - (по всем группам) отчет недельный по работе")
		self._botInternal.send_message(user.user_id, "кофе - убрать одну молнию")
		self._botInternal.send_message(user.user_id, "/getlight - добавить одну молнию")
		self._botInternal.send_message(user.user_id, "/here - зафиксировать приход на работу")
		self._botInternal.send_message(user.user_id, "/out - зафиксировать выход с работы")
		self._botInternal.send_message(user.user_id, "/stat - отчет недельный по работе")
		return HttpResponse('OK')
		
	def DebugMessage (self, group, message) :
		self._botInternal.send_message(group.group_id, message)

	def HiToUser (self, group, user) :
		self._botInternal.send_message(group.group_id, "Привет, *{}*.\nЯ бот Валера, буду следить за тем, когда ты пришел и ушел с работы. Надеюсь, мы подружимся;)\n*Добро пожаловать!*".format(user.GetDisplayName()), parse_mode = "Markdown")
		return HttpResponse('OK')
   
	def SendGoodBuy (self, group, user) :  	
		self._botInternal.send_message(group.group_id, "Пока, *{}*.\nНадеюсь мы еще увидимся...Буду скучать...".format(user.GetDisplayName()), parse_mode = "Markdown")
		return HttpResponse('OK')
	def Coffe(self, group, user, light, gfrom_message_id) :
		dateNow = timezone.now().date()
		if not WorkClock.objects.filter(user = user, day = dateNow).exists():
			self._botInternal.send_message(group.group_id, "Ты даже еще не на работе, какой кофе??")
		if WorkClock.objects.filter(user = user, day = dateNow).first().is_exit:
			self._botInternal.send_message(group.group_id, "Ты вроде не на работе, какой кофе??")
		else:
			light.count = light.count - 1
			if light.count < 0:
				light.count = 0
			light.save()
			self._botInternal.send_message(group.group_id, "Пришел вовремя и сварил кофе? Молодец! Ты снял еще одну молнию. Всего молний *%d*." % light.count, parse_mode = "Markdown", reply_to_message_id = gfrom_message_id)
		return HttpResponse('OK')
	def GetLight(self, group, light, gfrom_message_id) :
		light.count = light.count + 1
		light.save()
		self._botInternal.send_message(group.group_id, "Сегодня ты заработал еще одну молнию. Всего молний *{}*.".format(light.count) , parse_mode = "Markdown", reply_to_message_id = gfrom_message_id)
		return HttpResponse('OK')

	def Here(self, group, user, light, workclock, gfrom_message_id) :
		t = round(time())
 
		now = timezone.now()
		
		if not workclock.is_enter and not workclock.is_exit:
			workclock.last_enter = t
			workclock.is_enter = True
			journal = self._modelHelper.GetJournal(user)
			journal.date_in = now
			journal.workclock = workclock
			journal.save()
			
			self._botInternal.send_message(group.group_id, "Привет, *{}*.\nХорошего рабочего дня!".format(user.GetDisplayName()) , parse_mode = "Markdown", reply_to_message_id = gfrom_message_id)
			if now.hour > 8:
				light.count = light.count + 1
				light.save()
				self._botInternal.send_message(group.group_id, "Сегодня ты заработал еще одну молнию. Всего молний *{}*.".format(light.count), parse_mode = "Markdown", reply_to_message_id = gfrom_message_id)
			else:
				light.count = light.count - 1
				if light.count < 0:
					light.count = 0
				light.save()
				self._botInternal.send_message(group.group_id, "Сегодня ты снял еще одну молнию. Всего молний *{}*.".format(light.count) , parse_mode = "Markdown", reply_to_message_id = gfrom_message_id)
		elif workclock.is_exit:
			workclock.last_enter = t
			workclock.is_exit = False
			self._botInternal.send_message(group.group_id, "*{}*, хорошего продолжения рабочего дня!".format(user.GetDisplayName()), parse_mode = "Markdown", reply_to_message_id = gfrom_message_id)
		workclock.save()
		return HttpResponse('OK')
		
		
	def Out(self, group, user, workclock, gfrom_message_id) :
		now = timezone.now()
		t = round(time())
 
		if workclock.is_enter and not workclock.is_exit:
			journal = self._modelHelper.GetJournal(user)
			journal.date_out = now
			journal.save()
			workclock.is_exit = True
			workclock.last_exit = t
			workclock.seconds += workclock.last_exit - workclock.last_enter
			workclock.save()

			work_h = workclock.seconds // 3600
			work_m = (workclock.seconds - work_h*3600) // 60
			work_s = workclock.seconds - work_h*3600 - work_m*60

			self._botInternal.send_message(group.group_id, "Пока, *{}*.\nВремя работы: {}ч. {} мин. {} сек.\n".format(user.GetDisplayName(), work_h, work_m, work_s), parse_mode = "Markdown", reply_to_message_id = gfrom_message_id)
		return HttpResponse('OK')
		
		