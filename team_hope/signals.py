from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import UserProfile, UserIdentityInfo
from .utils import send_embracingostomylife_welcome_email, send_aliveandkicking_welcome_email, send_team_hope_welcome_email  


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
        UserIdentityInfo.objects.create(user=instance)
        send_embracingostomylife_welcome_email(instance)


@receiver(post_save, sender=UserProfile)
def send_team_hope_welcome(sender, instance, **kwargs):
    if instance.team_hope_all_complete and not instance.team_hope_training_complete:
        send_team_hope_welcome_email(instance.user)

@receiver(post_save, sender=UserProfile)
def send_aliveandkicking_welcome(sender, instance, **kwargs):
    if instance.subscribed_to_aliveandkicking and not instance.aliveandkicking_waiver_complete:
        send_aliveandkicking_welcome_email(instance.user)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.userprofile.save()
    instance.useridentityinfo.save()
