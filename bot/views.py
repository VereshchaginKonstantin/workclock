# -*- coding: utf-8 -*-
from __future__ import unicode_literals

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

from . groupLogic import *

def is_digit(string):
    if string.isdigit():
       return True
    else:
        try:
            float(string)
            return True
        except ValueError:
            return False

def isint(s):
    try:
        int(s)
        return True
    except ValueError:
        return False


def random_id():
  rid = ''
  for x in range(8): rid += random.choice(string.ascii_letters + string.digits)
  return rid


@csrf_exempt 
# Create your views here.
def bot(request):

	#kursDinar = KursDinar.objects.get(id=1).kurs
	#time.sleep(2)
	botTelegram = telebot.TeleBot('475168535:AAGBZZCxRdoDvsqjk0nXOy1gprdQHgyuUmo') #prod

	#print(request.body)
	#botTelegram.send_message(213974204, request.body.decode('utf-8'))
	data = json.loads(request.body.decode('utf-8'))
	modelHelper = ModelHelper() 
	dateHelper = DataHelper()
	report = Reports()
	report.SetBot(botTelegram) 
	botengine = BotEngineGroup()
	botengine.SetBot(botTelegram)
	gtext = ''
	try:

		if 'callback_query' in data:
			chat_id = data["callback_query"]["from"]["id"]
			callback_data = data["callback_query"]["data"]
			text = '' 
			file_id = ""
			gtext = callback_data.split(" ")[0]
			idGroup = callback_data.split(" ")[1]
			idUser = data["callback_query"]["from"]["id"]
			group = modelHelper.GetGroupById(idGroup)
			user = modelHelper.GetUserById(idUser, group)
			workclock = modelHelper.GetWorkClock(user)
			light = modelHelper.GetLightningByUser(user)
			gfrom_message_id = data["callback_query"]['message']['message_id']
			messageDateTime = dateHelper.ConvertDate(time.time())
			#if 'from' in data['callback_query']:
	
		elif 'message' in data:
			if data['message']['chat']['type'] == 'group':

				group = modelHelper.GetGroup(data)
				light = modelHelper.GetLightning(data, botengine)
				user = modelHelper.GetUser(data, botengine)
				workclock = modelHelper.GetWorkClock(user)
				messageDateTime = dateHelper.ConvertDate(data['message']['date'])
				
				#botengine.DebugMessage(group, "группа зафиксирована")
				
				if IsUserBot(user):
					return HttpResponse('OK')
				#botengine.DebugMessage(group, "пользователь зафиксирован")
				if 'new_chat_participant' in data['message']:
					return botengine.HiToUser(group, user)
				elif 'left_chat_participant' in data['message']:
					groupUserChatId = data['message']['left_chat_participant']['id']
					return botengine.SendGoodBuy(group, user)
				else:
					gfrom_message_id = data['message']['message_id']
					if 'text' in data['message']:
						gtext =  data['message']['text']
					else:
						return HttpResponse('OK')	
			elif data['message']['chat']['type'] == 'private':
				if 'text' in data['message']:
					userChatId = data['message']['from']['id']
					
					botTelegram.send_message(userChatId, "Давай общаться в группе ;) Я тут недавно, и пока еще стесняюсь. Я даже не смогу тебя зарегистрировать, так как все пользователи у меня по группкам разбиты :( Печалька. ")
					if data['message']['text'] == "Testing":
						if not userChatId is None:
							report.Test(userChatId)
					return HttpResponse('OK')	
		else:
			mes = 'Непонятное сообщение.'
			#botTelegram.send_message(chat_id, mes)
			return HttpResponse('OK')
			
		#botTelegram.send_message(213974204, gtext)
		if gtext is None:
			return HttpResponse('OK')
		elif gtext.lower() == "/help":			
			return botengine.Help(user)
			
		elif gtext.lower().startswith("/setstarttime"):
			return botengine.SetStartTime(user, int(gtext.lower().split(" ")[1]), int(gtext.lower().split(" ")[2]))
			
		elif gtext.lower() == "/news":			
			return HttpResponse('OK')
			
		elif gtext.lower() == "/destroy":
			modelHelper.Clear(user)
			return HttpResponse('OK')
			
		elif gtext.lower() == "/det":
			report.StatJournal(group, user)
			return HttpResponse('OK')	
			
		elif gtext.lower() == "/detprev":
			report.StatJournalPrev(group, user)
			return HttpResponse('OK')	
			 
		elif gtext.lower() == "/otpros":
			return botengine.MinusLight(group, user, light, gfrom_message_id, messageDateTime)
			 
				 
		elif gtext.lower() == "/sendlight": 
			report.SendLightPrivate()
			return HttpResponse('OK')	
			
		elif gtext.lower() == "/sendoverpriv": 
			report.OverWorkingPrivate()
			return HttpResponse('OK')

		elif gtext.lower() == "/testdecode":
			report.TestDecode()
			return HttpResponse('OK')
			
		elif gtext.lower() == "/week":
			report.reportWeeklyReport()
			return HttpResponse('OK')
	   
		elif gtext.lower() == "кофе":
			return botengine.Coffe(group, user, light, gfrom_message_id, messageDateTime)

		elif gtext.lower() == '/getlight':
			return botengine.GetLight(group, light, gfrom_message_id)
  
		elif gtext.lower() == 'тута' or gtext.lower() == '/here':
			return botengine.Here(group, user, light, workclock, messageDateTime)

		elif gtext.lower().startswith("/here") and (len(gtext.lower().split(" ")) == 3):
			messageDateTime = messageDateTime.replace(hour=int(gtext.lower().split(" ")[1]), minute=int(gtext.lower().split(" ")[2]))
			return botengine.Here(group, user, light, workclock, messageDateTime)
			
		elif gtext.lower().startswith("/out") and (len(gtext.lower().split(" ")) == 3):
			messageDateTime = messageDateTime.replace(hour=int(gtext.lower().split(" ")[1]), minute=int(gtext.lower().split(" ")[2]))
			return botengine.Out(group, user,  workclock, messageDateTime)
					
		elif gtext.lower() == 'нетута' or gtext.lower() == '/out':
			return botengine.Out(group, user, workclock,  messageDateTime)	
		 
		elif gtext.lower() == '/stat':
			report.Stat(group)
			return HttpResponse('OK') 
			
		elif gtext.lower() == '/statprev':
			report.StatPrev(group)
			return HttpResponse('OK') 
			
		elif gtext.lower() == '/allstat':
			report.AllTimeStat(group)
			return HttpResponse('OK')	
			
		else:
			botTelegram.send_message(213974204, "nothing")
			pass

		return HttpResponse('OK')

	except Exception as e:
		print(e)
		botTelegram.send_message(213974204, str(e))
		return HttpResponse('OK')

