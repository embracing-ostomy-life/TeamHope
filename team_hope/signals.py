from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from team_hope.utils.email_utils import (
    add_to_aliveandkicking_journey,
    add_to_teamhope_journey,
)
from .models import UserProfile


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
        # UserIdentityInfo.objects.get_or_create(user=instance)
        # send_embracingostomylife_welcome_email(instance)
        # send_embracingostomylife_welcome_email_html(instance)
        pass


@receiver(post_save, sender=UserProfile)
def send_team_hope_welcome(sender, instance, **kwargs):
    if instance.team_hope_all_complete and not instance.team_hope_training_complete:
        # send_team_hope_welcome_email(instance.user)
        # send_team_hope_welcome_email_html(instance.user)
        pass


@receiver(post_save, sender=UserProfile)
def send_aliveandkicking_welcome(sender, instance, **kwargs):
    if (
            not instance.subscribed_to_aliveandkicking
            and instance.aliveandkicking_waiver_complete
    ):
        add_to_aliveandkicking_journey(user=instance.user, userprofile=instance)
        profile = instance
        profile.subscribed_to_aliveandkicking = True
        profile.save()
        # send_aliveandkicking_welcome_email(instance.user)
        # send_aliveandkicking_welcome_email_html(instance.user)
    if not instance.subscribed_to_teamhope and instance.team_hope_docusign_complete:
        add_to_teamhope_journey(user=instance.user, userprofile=instance)
        profile = instance
        profile.subscribed_to_teamhope = True
        profile.save()


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.userprofile.save()
    # instance.useridentityinfo.save()
