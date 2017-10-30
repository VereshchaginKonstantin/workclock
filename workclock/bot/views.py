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

	botTelegram = telebot.TeleBot('475168535:AAGBZZCxRdoDvsqjk0nXOy1gprdQHgyuUmo') #prod

	#print(request.body)
	#botTelegram.send_message(354691583, request.body.decode('utf-8'))
	data = json.loads(request.body.decode('utf-8'))
	modelHelper = ModelHelper() 
	report = Reports()
	report.SetBot(botTelegram) 
	botengine = BotEngineGroup()
	botengine.SetBot(botTelegram)
	
	try:

		if 'callback_query' in data:
			chat_id = data["callback_query"]["from"]["id"]
			callback_data = data["callback_query"]["data"]
			text = ''
			file_id = ""
		elif 'message' in data:
			if data['message']['chat']['type'] == 'group':

				group = modelHelper.GetGroup(data)
				light = modelHelper.GetLightning(data, botengine)
				user = modelHelper.GetUser(data, botengine)
				workclock = modelHelper.GetWorkClock(user)
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
					gtext =  data['message']['text']
			elif data['message']['chat']['type'] == 'private':
				if 'text' in data['message']:
					userChatId = data['message']['from']['id']
					botTelegram.send_message(userChatId, "Давай общаться в группе ;) Я тут недавно, и пока еще стесняюсь. Я даже не смогу тебя зарегистрировать, так как все пользователи у меня по группкам разбиты :( Печалька. ")
					return HttpResponse('OK')	
		else:
			mes = 'Непонятное сообщение.'
			#botTelegram.send_message(chat_id, mes)
			return HttpResponse('OK')

		if gtext.lower() == "/help":			
			return botengine.Help(user)
			
		if gtext.lower() == "/destroy":
			modelHelper.Clear(user)
			return HttpResponse('OK')
			
		if gtext.lower() == "/det":
			report.StatJournal(group, user, gfrom_message_id)
			return HttpResponse('OK')	
			
		if gtext.lower() == "/over":
			report.OverWorking()
			return HttpResponse('OK')
			
		if gtext.lower() == "/week":
			report.reportWeeklyReport()
			return HttpResponse('OK')
	   
		if gtext.lower() == "кофе":
			return botengine.Coffe(group, user, light, gfrom_message_id)

		if gtext.lower() == '/getlight':
			return botengine.GetLight(group, light, gfrom_message_id)
  
		if gtext.lower() == 'тута' or gtext.lower() == '/here':
			return botengine.Here(group, user, light, workclock, gfrom_message_id)


		elif gtext.lower() == 'нетута' or gtext.lower() == '/out':
			return botengine.Out(group, user, workclock, gfrom_message_id)	
		 
		elif gtext.lower() == '/stat':
			report.Stat(group)
			return HttpResponse('OK')
		else:
			pass

		return HttpResponse('OK')

	except Exception as e:
		print(e)
		botTelegram.send_message(213974204, str(e))
		return HttpResponse('OK')

