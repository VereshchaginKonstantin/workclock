from django.db import models

# Create your models here.

class group(models.Model):
	group_id = models.BigIntegerField()
	group_name = models.CharField(max_length=50, null=True, blank = True)

	def __str__(self):
		return 'id = ' + str(self.id) + " " + self.fio + " " + self.username

	class Meta:
		verbose_name 		= 'Telegram Group'
		verbose_name_plural = 'Telegram Group'

class groupUser(models.Model):
	user_id 		= models.BigIntegerField()
	start_hour = models.IntegerField(default = 9)
	start_minute = models.IntegerField(default = 0)
	group 			= models.ForeignKey(group, null=True, blank = True) 
	step			= models.CharField(max_length=50, null=True, blank = True)
	username 		= models.CharField(max_length=120, null=True, blank = True)
	fio				= models.CharField(max_length=120, null=True, blank = True)

	date_in 		= models.DateTimeField(auto_now_add = True, auto_now = False, null=True, blank = True)

	# balance					= models.FloatField(null=True, blank = True, default = 0)
	# ref_count				= models.IntegerField(null=True, blank = True, default = 0)
	# parent 					= models.IntegerField(null=True, blank = True, default = 0)

	# lang 					= models.CharField(max_length=50, null=True, blank = True)

	def GetDisplayName(self) :
		if self.username == "":
			name = self.fio.encode('utf8')
		else:
			name = self.username
		return name

	def IsBot(self) :
		return self.GetDisplayName() == 'WorkingStatisticBot'

	def __str__(self):
		return 'id = ' + str(self.id) + " " + self.fio + " " + self.username

	class Meta:
		verbose_name 		= 'Telegram Group User'
		verbose_name_plural = 'Telegram Group User'


class WorkClock(models.Model):
	day	 			= models.DateField(null=True, blank = True)
	user 			= models.ForeignKey(groupUser, null=True, blank = True)

	is_enter		= models.BooleanField(default = False)
	is_exit			= models.BooleanField(default = False)
	last_enter 		= models.BigIntegerField(null=True, blank = True)
	last_exit 		= models.BigIntegerField(null=True, blank = True)
	seconds			= models.BigIntegerField(null=True, blank = True, default = 0)


class Lightning(models.Model):
	user = models.ForeignKey(groupUser, null=True, blank = True)
	count	= models.BigIntegerField(null=True, blank = True)
	class Meta:
		verbose_name 		= 'Lightning'
		verbose_name_plural = 'Lightning'
	
class Otpros(models.Model):
	user = models.ForeignKey(groupUser, null=True, blank = True)
	date_in 	= models.DateTimeField(null=True, blank = True)
	
	class Meta:
		verbose_name 		= 'Otpros'
		verbose_name_plural = 'Otproses'	
	
class Journal(models.Model):
	user = models.ForeignKey(groupUser, null=True, blank = True)
	date_in 		= models.DateTimeField(null=True, blank = True)
	date_out 		= models.DateTimeField(null=True, blank = True)
	workclock 		= models.ForeignKey(WorkClock, null=True, blank = True)
	
	class Meta:
		verbose_name 		= 'Journal'
		verbose_name_plural = 'Journal'
