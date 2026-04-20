from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid
from django.conf import settings

import random
from django.utils import timezone


class CustomUser(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    email = models.EmailField(unique=True)
    is_email_verified = models.BooleanField(default=False)
    email_otp = models.CharField(max_length=6, null=True, blank=True)
    otp_last_sent = models.DateTimeField(null=True, blank=True) 
    
    is_host = models.BooleanField(default=False)
    phone = models.CharField(max_length=15,blank=True,null=True)
    is_phone_verified = models.BooleanField(default=False)
    address = models.CharField(max_length=255, blank=True, null=True)
    
    
    


class Profile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,  # ✅ use this instead of 'auth.User'
        on_delete=models.CASCADE
    )
    image = models.ImageField(upload_to='profile_pics/', default='default.avif')

    def __str__(self):
        return self.user.username


class OTP(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_expired(self):
        return timezone.now() > self.created_at + timezone.timedelta(minutes=5)
