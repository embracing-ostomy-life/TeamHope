from django.contrib import admin
from .models import UserProfile, UserIdentityInfo

admin.site.register(UserProfile)
admin.site.register(UserIdentityInfo)
# Register your models here.
