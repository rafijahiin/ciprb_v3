from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('UNFPA_ADMIN', 'UNFPA Admin'),
        ('CIPRB_ADMIN', 'CIPRB Admin'),
        ('PHD_USER', 'PHD User'),
        ('BONDHU_USER', 'Bondhu User'),
        ('VIEWER', 'Viewer (Read Only)'),
    ]
    ORG_CHOICES = [
        ('UNFPA', 'UNFPA'),
        ('CIPRB', 'CIPRB'),
        ('PHD', 'PHD'),
        ('Bondhu', 'Bondhu'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='VIEWER')
    organisation = models.CharField(max_length=20, choices=ORG_CHOICES, default='CIPRB')

    def is_unfpa_admin(self):
        return self.role == 'UNFPA_ADMIN'

    def is_org_admin(self):
        return self.role in ('UNFPA_ADMIN', 'CIPRB_ADMIN')

    def can_enter_data(self):
        return self.role != 'VIEWER'

    def __str__(self):
        return f"{self.user.username} ({self.role})"
