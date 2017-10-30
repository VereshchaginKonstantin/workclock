from django.contrib import admin
from .models import *
# Register your models here.
from django.contrib.auth.models import Group, User

admin.site.unregister(Group)
admin.site.unregister(User)

# class botUserAdmin(admin.ModelAdmin):
#     list_display = ["__str__", "parent", "ref_count","balance"]
   
# admin.site.register(botUser, botUserAdmin)

admin.site.register(group)

admin.site.register(groupUser)

admin.site.register(WorkClock)

admin.site.register(Lightning)

admin.site.register(Journal)

