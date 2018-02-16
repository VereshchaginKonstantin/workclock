# -*- coding: utf-8 -*-
 
#import feedparser
from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import telebot
import json
from time import sleep, time
import time
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
import locale 
from dateutil.parser import parse
import urllib.request


def IsWorkingDay():
    	dataHelper = DataHelper()
    	dataInFormat = "{:%Y%m%d}".format(dataHelper.GetNow())
    	answer = urllib.request.urlopen("https://isdayoff.ru/{0}?cc=ru".format(dataInFormat)).read()
		return answer == '0';

def IsUserBot(user):
	return user.GetDisplayName() == 'WorkingStatisticBot'

class DataHelper:
	def GetNow(self) :
		current_tz = timezone.get_current_timezone()
		now = timezone.now()		
		local = current_tz.normalize(now.astimezone(current_tz))
		return local
		
		
	def ConvertDate(self, unixTime) :
		current_tz = timezone.get_current_timezone() 	
		datetime1 = datetime.fromtimestamp(unixTime)
		date2 = current_tz.localize(datetime1, is_dst=True)
		local = current_tz.normalize(date2)
		return local
		

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
 
	def GetLightningByUser(self, user):
		if not Lightning.objects.filter(user = user).exists():
			Lightning.objects.create(user = user, count = 0)
		return Lightning.objects.filter(user = user).first()
		
	def GetGroupById (self, idUser) :
		return group.objects.filter(group_id = idUser).first()
	def GetUserById (self, idUser, group) :
		return groupUser.objects.filter(user_id = idUser).filter(group = group).first()
	
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

class ReportUserInfo(object):
	seconds = 0
	lightCount = 0
	guser = 0
	otprosCount = 0
	pass

		
class Reports:
	_botInternal = 0
	def SetBot(self,  botInside) :
		self._botInternal = botInside 
	
	def Test(self, user_id):
		self.SendLight(user_id)
		self.WeeklyReport(user_id)
		self.News(user_id)
		
	def TestDecode(self):
		self._botInternal.send_message(213974204, u'test') 
 
				
	def News(self, user_id  = None) :
		dd = 4
		#d = feedparser.parse('https://news.yandex.ru/science.rss')
		#randomNews = random.randint(0, len(d.entries) - 1)
		#news f= d.entries[randomNews]
		#for group1 in group.objects.all():	
		#if user_id is None:
		#		self._botInternal.send_message(group1.group_id, news.description, parse_mode = "Markdown")
		#	else:
		#		self._botInternal.send_message(user_id, news.description, parse_mode = "Markdown")


	def SendEvent(self):
		d = timezone.now()
		for event in Event.objects.all():
			yearNow = d.year
			dateEvent = event.date_event.replace(year = yearNow)
			tdelta = dateEvent - d
			daysRest = tdelta.days
			if daysRest == 1 or daysRest == 8:
				for user in groupUser.objects.all():
					if user.group == event.user.group:
						if user != event.user:
							try:
								self._botInternal.send_message(user.user_id, '{} - {} - {}'.format(event.user.GetDisplayName(), event.date_event , event.eventMessage.encode('utf8')) , parse_mode = "Markdown")
							except Exception as e:
								self._botInternal.send_message(213974204, str(e))
		
	def SendUserId(self, userG):
		for user in groupUser.objects.all():
			if user.group == userG.group:
				self._botInternal.send_message(userG.user_id, "{} - {}".format(user.GetDisplayName(), user.id), parse_mode = "Markdown")

	
	def SendLight(self, user_id = None):
		d = timezone.now().date()  
		mes = "МОЛНИИ!!!"
		for group1 in group.objects.all():
			if user_id is None:
				keyboard = telebot.types.InlineKeyboardMarkup()
				url_button = telebot.types.InlineKeyboardButton(text="Прийти", callback_data="/here {}".format(group1.group_id))
				keyboard.add(url_button) 
				self._botInternal.send_message(group1.group_id, mes, reply_markup = keyboard)
			else:
				keyboard = telebot.types.InlineKeyboardMarkup()
				url_button = telebot.types.InlineKeyboardButton(text=u"Прийти ({})".format(group1.group_name), callback_data="/here {}".format(group1.group_id))
				keyboard.add(url_button) 
				self._botInternal.send_message(user_id, mes, reply_markup = keyboard)
				
	def SendLightPrivate(self):
		mes = "Доброе утро, {}!"
		modelHelper = ModelHelper()
		mesError = "Не могу достучаться, и пожелать доброе утро {}. Пусть свяжется со мной в личке."
		for group1 in group.objects.all():
			for user1 in groupUser.objects.filter(group = group1):
				keyboard = telebot.types.InlineKeyboardMarkup()
				url_button = telebot.types.InlineKeyboardButton(text=u"Прийти ({})".format(group1.group_name), callback_data="/here {}".format(group1.group_id))
				keyboard.add(url_button)
				try:
					if not user1.IsBot():
						workclock = modelHelper.GetWorkClock(user1)
						if not workclock.is_enter and not workclock.is_exit:
							self._botInternal.send_message(user1.user_id, mes.format(user1.GetDisplayName()), reply_markup = keyboard) 
				except Exception as e:
					self._botInternal.send_message(group1.group_id, mesError.format(user1.GetDisplayName()), parse_mode = "Markdown")  
				

	def StatJournal(self, group, user):
		mesError = "Не могу достучаться до {}. Пусть свяжется со мной в личке."
		locale.setlocale(locale.LC_ALL, 'ru_RU.UTF-8')
		dateNow = timezone.now()
		dweek = dateNow.weekday()
		d_start = dateNow - timedelta(days = dweek)
		d_start = d_start.replace(hour=0, minute=0)
		dateNow = dateNow.replace(hour=23, minute=59)
		self.PtintJournal(group, user, d_start, dateNow)

	def PtintJournal(self, group, user, d_start, dateEnd):
		self._botInternal.send_message(user.user_id, "{: %Y-%m-%d} -> {: %Y-%m-%d}".format(d_start, dateEnd))
		mes = "*Подробная статистика для вас:*\n"
		for journalEntry in sorted(Journal.objects.filter(user=user, date_in__gte = d_start, date_in__lte = dateEnd), key= lambda x: x.date_in.isoweekday(), reverse=False):
			if not journalEntry.date_in is None:
				current_tz = timezone.get_current_timezone()
				local = current_tz.normalize(journalEntry.date_in.astimezone(current_tz))
				mes += "{} {: %Y-%m-%d (%H:%M} -".format(journalEntry.date_in.strftime('%a'), local) 
			if not journalEntry.date_out is None:
				local = current_tz.normalize(journalEntry.date_out.astimezone(current_tz))
				mes += " {:%H:%M}) ".format(local)
			seconds = journalEntry.workclock.seconds
			if seconds is None:
				seconds = 0
			seconds -= 45 * 60
			work_h = seconds // 3600
			work_m = (seconds - work_h*3600) // 60
			mes += " *{}ч.{}м.*\n".format(work_h, work_m)		
		try:
			self._botInternal.send_message(user.user_id, mes, parse_mode = "Markdown")
		except Exception as e:
			self._botInternal.send_message(group.group_id, mesError.format(user.GetDisplayName().encode('utf8')), parse_mode = "Markdown") 

	
	def StatJournalPrev(self, group, user):
		mesError = "Не могу достучаться до {}. Пусть свяжется со мной в личке."
		dateNow = timezone.now()
		dweek = dateNow.weekday()
		d_start = dateNow - timedelta(days = (dweek+7))
		d_end = dateNow - timedelta(days = (dweek+1))
		
		d_start = d_start.replace(hour=0, minute=0)
		d_end = d_end.replace(hour=23, minute=59)
		self.PtintJournal(group, user, d_start, d_end)
	
	def Stat(self, group):
		dateNow = timezone.now()
		dweek = dateNow.weekday()
		d_start = dateNow - timedelta(days = dweek)
		d_start = d_start.replace(hour=0, minute=0)
		dateNow = dateNow.replace(hour=23, minute=59)
		self.StatPrint(group, d_start, dateNow)

	def StatPrev(self, group):
		dateNow = timezone.now()
		dweek = dateNow.weekday()
		d_start = dateNow - timedelta(days = (dweek+7))
		d_end = dateNow - timedelta(days = (dweek+1))
		
		d_start = d_start.replace(hour=0, minute=0)
		d_end = d_end.replace(hour=23, minute=59)
		self.StatPrint(group, d_start, d_end)
		
	def AllTimeStat(self, group):
		dateNow = timezone.now()
		statisticArray = []
		for guser in groupUser.objects.filter(group=group):
			reportUserInfo = ReportUserInfo()
			seconds = WorkClock.objects.filter(user = guser).aggregate(Sum('seconds'))['seconds__sum']
			if seconds is None:
				seconds = 0 
			reportUserInfo.seconds = seconds
			reportUserInfo.guser= guser
			reportUserInfo.otprosCount = len(Otpros.objects.filter(user = guser))
			if not IsUserBot(guser):
				statisticArray.append(reportUserInfo)
				lightcurr = Lightning.objects.filter(user = guser).first()
				if not lightcurr is None:
					reportUserInfo.lightCount = lightcurr.count
				else:
					reportUserInfo.lightCount = 0
		self.StatPrint(statisticArray, group)

	def StatPrint(self, group, d_start, dateNow):
		statisticArray = []
		self._botInternal.send_message(group.group_id, "{: %Y-%m-%d} -> {: %Y-%m-%d}".format(d_start, dateNow))
		for guser in groupUser.objects.filter(group=group):
			reportUserInfo = ReportUserInfo()

			seconds = WorkClock.objects.filter(user = guser, day__gte = d_start, day__lte = dateNow).aggregate(Sum('seconds'))['seconds__sum']
			if seconds is None:
				seconds = 0 
			reportUserInfo.seconds = seconds
			reportUserInfo.guser= guser
			reportUserInfo.otprosCount = len(Otpros.objects.filter(user = guser))
			
			if not IsUserBot(guser):
				statisticArray.append(reportUserInfo)
				lightcurr = Lightning.objects.filter(user = guser).first()
				if not lightcurr is None:
					reportUserInfo.lightCount = lightcurr.count
				else:
					reportUserInfo.lightCount = 0
		self.StatPrintOut(statisticArray, group)

	
	def StatPrintOut(self, reportItems, group):						
		mes = "*Статистика:*\n"
		for info in sorted(reportItems, key=lambda x: x.guser.fio, reverse=True):
			seconds = info.seconds
			work_h = seconds // 3600
			work_m = (seconds - work_h*3600) // 60
			work_s = seconds - work_h*3600 - work_m*60
			mes +=  "*{}*, работал: {}:{}:{}. ".format(info.guser.GetDisplayName(), work_h, work_m, work_s)
			mes += "М: *{}*.\n".format(info.lightCount)
			
		self._botInternal.send_message(group.group_id, mes, parse_mode = "Markdown")
		mes = "*\n ******** *\n *Топ любителей опоздать:*\n"
		for info in sorted(reportItems, key=lambda x: x.lightCount, reverse=True)[:3]:
			mes += "*{}*, молнии: *{}*.\n".format(info.guser.GetDisplayName(), info.lightCount)

		self._botInternal.send_message(group.group_id, mes, parse_mode = "Markdown")
		
		mes = "*\n ******** *\n *Топ любителей отпроситься:*\n"
		for info in sorted(reportItems, key=lambda x: x.otprosCount, reverse=True)[:3]:
			mes += "*{}*, отпрашивался  *{}* раз.\n".format(info.guser.GetDisplayName(), info.otprosCount)
		self._botInternal.send_message(group.group_id, mes, parse_mode = "Markdown")
			

		mes = "*\n ******** *\n *Топ трудяг:*\n"
		for info in sorted(reportItems, key=lambda x: x.seconds, reverse=True)[:3]:
			seconds = info.seconds
			work_h = seconds // 3600
			work_m = (seconds - work_h*3600) // 60
			work_s = seconds - work_h*3600 - work_m*60
			mes +=  " *{}*, работал: {}:{}:{}. \n".format(info.guser.GetDisplayName(), work_h, work_m, work_s)
		self._botInternal.send_message(group.group_id, mes, parse_mode = "Markdown")

	def WhoIsThere(self, group):
		d = timezone.now().date()  
		mes = " "
		for user in groupUser.objects.filter(group=group):
			if  WorkClock.objects.filter(user = user, day=d).exists():
    			#workclockObject = WorkClock()
				workclockObject = WorkClock.objects.filter(user = user, day=d).first()
				mes += "*{}*, находится *{}* \n".format(user.GetDisplayName(), workclockObject.currentLocation.encode('utf8'))
			else:
				mes += "*{}*, не отмечался сегодня, хотя не в отпуске. \n".format(user.GetDisplayName())    				
		try:
			if mes == " ":
				self._botInternal.send_message(group.group_id, 'Никого нет', parse_mode = "Markdown")
			else:
				self._botInternal.send_message(group.group_id, mes, parse_mode = "Markdown")
		except Exception as e:
			self._botInternal.send_message(213974204, str(e)) 
		
	def OverWorkingPrivate(self):
		mesError = "Не могу достучаться до {}. Пусть свяжется со мной в личке."
		d = timezone.now().date()  
		mes = "Пора домой: "
		for group1 in group.objects.all():
			for user in groupUser.objects.filter(group=group1):
				
				if  WorkClock.objects.filter(user = user, day=d, is_exit = False, is_enter = True).exists():
					try:
						keyboard = telebot.types.InlineKeyboardMarkup()
						url_button = telebot.types.InlineKeyboardButton(text=u"Уйти из {}".format(group1.group_name), callback_data="/out {}".format(group1.group_id))
						keyboard.add(url_button) 
						self._botInternal.send_message(user.user_id, mes, reply_markup = keyboard)
					except Exception as e:
						self._botInternal.send_message(group1.group_id, mesError.format(user.GetDisplayName()), parse_mode = "Markdown") 
		 	
	def WeeklyReport(self, user_id = None) :
		for group1 in group.objects.all():
			self.Stat(group1)
	
class BotEngineGroup:
	_botInternal = 0
	_modelHelper = 0
	def SetBot(self,  botInside) :
		self._botInternal = botInside
		self._modelHelper = ModelHelper()

	def RegEvent(self, query):
		try:
			
			userRealId = int(query.split(' ')[0])
			dateEvent = query.split(' ')[1]
			messageEvent = query[12:]
			
			for user in groupUser.objects.all():
				if user.id == userRealId:
					dt = parse(dateEvent, dayfirst=True)
					dt = dt.replace(hour=14, minute=0)
					event = Event.objects.create(user = user, date_event = dt, eventMessage = messageEvent) 
			for event in Event.objects.all():
				self._botInternal.send_message(213974204, "{} - {} - {}".format(event.user.GetDisplayName(), event.date_event ,event.eventMessage.encode('utf8')) , parse_mode = "Markdown")  
		except Exception as e:
			print(e)
			self._botInternal.send_message(213974204, str(e))
		
	def SetStartTime(self, user, startHour, startMinute):
		
		user.start_hour = startHour
		user.start_minute = startMinute
		user.save()
		self._botInternal.send_message(user.group.group_id, "Для *{}* установлено время начало работы {}:{}.".format(user.GetDisplayName(), startHour, startMinute), parse_mode = "Markdown")
		return HttpResponse('OK')
		
			
	def SetOtpusk(self, user, isOtpusk):	
		user.isOtpusk = isOtpusk
		user.save()
		if isOtpusk:
			self._botInternal.send_message(user.group.group_id, "*{}* ушел в отпуск.".format(user.GetDisplayName()), parse_mode = "Markdown")
		else:
			self._botInternal.send_message(user.group.group_id, "*{}* вернулся из отпуска.".format(user.GetDisplayName()), parse_mode = "Markdown")
		return HttpResponse('OK')

	def Help(self, user) :
		mes = ''
		mes += "/det - детальный план.\n"
		mes += "/over - (по всем группам) рассылает всем сообщение о переработке, что бы вышли если в системе.\n" 
		mes += "/week - (по всем группам) отчет недельный по работе.\n" 
		mes += "кофе - убрать одну молнию.\n" 
		mes += "/getlight - добавить одну молнию.\n" 
		mes += "/here - зафиксировать приход на работу.\n" 
		mes += "/here hour minute - зафиксировать приход на работу с указанием часов и минут, когда пришел.\n" 
		mes += "/out - зафиксировать выход с работы.\n" 
		mes += "/out hour minute - зафиксировать выход с работы с указанием часов и минут, когда ушел.\n" 
		mes += "/stat - отчет недельный по работе.\n" 
		mes += "/otpros - отпроситься(снимает одну молнию).\n" 
		
		self._botInternal.send_message(user.user_id, mes)
		return HttpResponse('OK')
		
	def DebugMessage (self, group, message) :
		self._botInternal.send_message(group.group_id, message)

	def HiToUser (self, group, user) :
		self._botInternal.send_message(group.group_id, "Привет, *{}*.\nЯ бот Валера, буду следить за тем, когда ты пришел и ушел с работы. Надеюсь, мы подружимся;)\n*Добро пожаловать!*".format(user.GetDisplayName()), parse_mode = "Markdown")
		return HttpResponse('OK')
   
	def SendGoodBuy (self, group, user) :  	
		self._botInternal.send_message(group.group_id, "Пока, *{}*.\nНадеюсь мы еще увидимся...Буду скучать...".format(user.GetDisplayName()), parse_mode = "Markdown")
		return HttpResponse('OK')
	def Coffe(self, group, user, light, gfrom_message_id, messageDateTime) :
		dateNow = messageDateTime
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
	def SetLight(self, group, light, ligthCount, gfrom_message_id):
		light.count = ligthCount
		light.save()
		self._botInternal.send_message(group.group_id, "Установлено молний *%d*." % light.count, parse_mode = "Markdown", reply_to_message_id = gfrom_message_id)
		return HttpResponse('OK')
		
	def MinusLight(self, group, user, light, gfrom_message_id, messageDateTime) :
		light.count = light.count - 1
		if light.count < 0:
			light.count = 0
		light.save()
		
		Otpros.objects.create(user = user, date_in = messageDateTime)
		
		self._botInternal.send_message(group.group_id, "Лишняя молния? Ну давай уберем. Всего молний *%d*." % light.count, parse_mode = "Markdown", reply_to_message_id = gfrom_message_id)
		return HttpResponse('OK')		

	def GetLight(self, group, light, gfrom_message_id) :
		light.count = light.count + 1
		light.save()
		self._botInternal.send_message(group.group_id, "Сегодня ты заработал еще одну молнию. Всего молний *{}*.".format(light.count) , parse_mode = "Markdown", reply_to_message_id = gfrom_message_id)
		return HttpResponse('OK')

	def HerePlace(self, workclock, place) :
		workclock.currentLocation = place
		workclock.save()
		return HttpResponse('OK')
		
	def Here(self, group, user, light, workclock, messageDateTime) :
		t = round(time.mktime(messageDateTime.timetuple()))
		now = messageDateTime
		allmess = ""
		workclock.currentLocation = '-'
		if not workclock.is_enter and not workclock.is_exit:
			workclock.last_enter = t
			workclock.is_enter = True
			journal = self._modelHelper.GetJournal(user)
			journal.date_in = messageDateTime
			journal.workclock = workclock
			journal.save()
			
			allmess += "На месте, *{}*.".format(user.GetDisplayName())
			if (now.hour == user.start_hour and now.minute >= user.start_minute) or (now.hour > user.start_hour):
				allmess += " + молния. *{}*.".format(light.count)
			else:
				light.count = light.count - 1
				if light.count < 0:
					light.count = 0
				light.save()
				allmess += " - молния. Если хотите снимать молнии, отмечайтесь вовремя! :p *{}*.".format(light.count)
		elif workclock.is_exit:
			workclock.last_enter = t
			workclock.is_exit = False
			allmess += "*{}*, вернулся!".format(user.GetDisplayName())
		workclock.save()
		if allmess != "":
			self._botInternal.send_message(group.group_id, allmess, parse_mode = "Markdown")
		return HttpResponse('OK')
		
		
	def Out(self, group, user, workclock, messageDateTime) :
		now = messageDateTime
		t = round(time.mktime(messageDateTime.timetuple()))
 
		if workclock.is_enter and not workclock.is_exit:
			journal = self._modelHelper.GetJournal(user)
			journal.date_out = now
			journal.save()
			workclock.currentLocation = 'Не на работе'
			workclock.is_exit = True
			workclock.last_exit = t
			workclock.seconds += workclock.last_exit - workclock.last_enter
			workclock.save()

			work_h = workclock.seconds // 3600
			work_m = (workclock.seconds - work_h*3600) // 60
			work_s = workclock.seconds - work_h*3600 - work_m*60

			self._botInternal.send_message(group.group_id, "Пока, *{0}*.\nВремя работы: *{1:d}ч.{2:d}м.* \n".format(user.GetDisplayName(), int(work_h), int(work_m)), parse_mode = "Markdown")
		return HttpResponse('OK')
		
		