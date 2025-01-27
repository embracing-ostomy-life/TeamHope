from django.contrib import admin
from .models import UserProfile, UserIdentityInfo

admin.site.register(UserIdentityInfo)
# Register your models here.


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("id", "surgery_date", "surgery_type", "teamhope_member_role")
    list_filter = ("surgery_date", "surgery_type", "teamhope_member_role")
