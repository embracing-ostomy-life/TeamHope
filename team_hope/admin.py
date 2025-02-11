from django.contrib import admin
from .models import UserProfile, UserIdentityInfo

admin.site.register(UserIdentityInfo)
# Register your models here.


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "get_first_name",
        "get_last_name",
        "teamhope_member_role",
        "surgery_type",
        "surgery_date",
        "age",
        "gender",
        "relationship_status",
        "primary_language",
        "hobbies",
        "bio",
        "team_hope_docusign_complete",
        "team_hope_training_complete",
    )
    list_filter = (
        "teamhope_member_role",
        "surgery_date",
        "surgery_type",
        "age",
        "gender",
        "relationship_status",
        "primary_language",
        "team_hope_docusign_complete",
        "team_hope_training_complete",
    )

    readonly_fields = ("get_email", "get_first_name", "get_last_name")

    def get_username(self, obj):
        return obj.user.username

    get_username.admin_order_field = "user__username"  # Allows column sorting
    get_username.short_description = "Username"

    def get_first_name(self, obj):
        return obj.user.first_name

    get_first_name.admin_order_field = "user__first_name"
    get_first_name.short_description = "First Name"

    def get_last_name(self, obj):
        return obj.user.last_name

    get_last_name.admin_order_field = "user__last_name"
    get_last_name.short_description = "Last Name"

    def get_email(self, obj):
        return obj.user.email

    get_email.admin_order_field = "user__email"
    get_email.short_description = "Email"
