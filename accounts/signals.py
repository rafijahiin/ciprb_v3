from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import UserProfile


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        # Superusers get UNFPA_ADMIN role automatically
        role = 'UNFPA_ADMIN' if instance.is_superuser else 'VIEWER'
        org = 'UNFPA' if instance.is_superuser else 'CIPRB'
        UserProfile.objects.get_or_create(user=instance, defaults={'role': role, 'organisation': org})

@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()
