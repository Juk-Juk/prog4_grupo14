""" from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Profile

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    instance.profile.save() """

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Profile

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        # Create a profile when a new user is created
        Profile.objects.create(user=instance)
    else:
        # If the User already exists, check if the Profile exists
        if not hasattr(instance, 'profile'):
            # If the profile does not exist, create it
            Profile.objects.create(user=instance)
        # If the profile exists, save it
        else:
            instance.profile.save()

