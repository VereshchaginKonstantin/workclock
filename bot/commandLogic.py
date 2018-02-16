# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import telebot
import json
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

def ProcessCommand(botengine, report, workclock, user, group, gtext, light, gfrom_message_id, messageDateTime):
	if gtext is None:
		return HttpResponse('OK')
#	elif gtext.lower() == "/help":			
#		return botengine.Help(user)
		
	elif gtext.lower().startswith("/setstarttime"):
		return botengine.SetStartTime(user, int(gtext.lower().split(" ")[1]), int(gtext.lower().split(" ")[2]))
		
	elif gtext.lower() == "/news":			
		return HttpResponse('OK')
 
	elif gtext.startswith('/otpusk'): 
		return botengine.SetOtpusk(user, True)

	elif gtext.startswith('/work'): 
		return botengine.SetOtpusk(user, False)

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
		 
	elif gtext.startswith('/setlight'): 
		return botengine.SetLight(group, light, int(gtext[9:]), gfrom_message_id)
		
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

		
	elif gtext.lower() == '/who':
		report.WhoIsThere(group)
		return HttpResponse('OK')
		
	elif gtext.lower() == '/sendevent':
		report.SendEvent()
		return HttpResponse('OK')		
			
			
	elif gtext.startswith('/getuserid'):
		report.SendUserId(user)
		return HttpResponse('OK')
		
	elif gtext.startswith('/place'):
		return botengine.HerePlace(workclock, gtext[6:])
		
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
		#botTelegram.send_message(213974204, "nothing")
		#botTelegram.send_message(213974204, "nothing")
		pass

	return HttpResponse('OK')
