from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User

class UserType(models.TextChoices):
    MAYBE   = 'maybe',  _('Considering Surgery')
    OST     = 'ost',    _('Ostomate')
    CARE    = 'care',   _('Caregiver')
    MEDPRO  = 'medpro', _('Medical Professional')

# Create your models here.

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # Add your custom fields here (e.g., department, user type, etc.)
    user_type   = models.CharField(max_length=10, choices=UserType.choices)
    country     = models.CharField(max_length=50, null=True, blank=True)
    state       = models.CharField(max_length=50, null=True, blank=True)
    journey     = models.TextField(max_length=4001, null=True, blank=True)

    subscribed_to_email_updates     = models.BooleanField(null=True)
    subscribed_to_30_day_recovery   = models.BooleanField(null=True)
    agreed                          = models.BooleanField(null=True)
    registered                      = models.BooleanField(null=True)

class UserIdentityInfo(models.Model):  # Renamed from SSOInfo for better clarity
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    date_of_birth   = models.DateField(null=True, blank=True)  # Add the DOB field here
    uuid            = models.CharField(max_length=64, null=True, unique=True)
    phone           = models.CharField(max_length=17, null=True, blank=True)
