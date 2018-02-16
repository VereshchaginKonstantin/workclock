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
from groupLogic import *


class ReportLights(object):
	lights = 0
	user = 0
	pass

class LightEngine:
    	_botInternal = 0
	def SetBot(self,  botInside) :
		self._botInternal = botInside
			
	def SetLightsAndSendButton(self):
    	helper = DataHelper()
		now = helper.GetNow()
		modelHelper = ModelHelper()
		
	 	for group1 in group.objects.all():
    		reportArray = []
			for user1 in groupUser.objects.filter(group = group1):
    			light = modelHelper.GetLightningByUser(user1)
				if (now.hour == user1.start_hour and now.minute >= user1.start_minute):
    				light.count = light.count + 1
					light.save()
					reportLights = ReportLights()
					reportLights.user = user1
					reportLights.lights = light.count
					reportArray.append(reportLights)
			this.SendMessage(reportArray, group1)

	def SendMessage(self,reportArray, group):		 
		mes = "*\n ******** *\n *На текущий момент опоздали:*\n"
		for info in sorted(reportArray, key=lambda x: x.lights, reverse=True):
			mes +=  " *{}*, молний: {}. \n".format(info.user.GetDisplayName(), info.lights)
		self._botInternal.send_message(group.group_id, mes, parse_mode = "Markdown")
