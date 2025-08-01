from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator
import datetime
from .constants import *
from django.utils import timezone

class CustomUser(AbstractUser):
    sex = models.CharField(max_length=10, choices=SEX_CHOICES)
    function = models.CharField(max_length=40, blank=True)
    quality = models.CharField(max_length=40, blank=True)
    role = models.CharField(max_length=40, choices=USERS_ROLES)
    # linked_agent_class = models.CharField(max_length=15)

    def __str__(self) -> str:
        return self.username + ' - '+ self.role

class ConfirmToken(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    kind = models.CharField(max_length=20, choices=TOKEN_TYPES)
    token_hash = models.BinaryField(blank=True)
    token_epires_at = models.DateTimeField(default=datetime.datetime.now)
    extra_data = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ('kind', 'user',)
