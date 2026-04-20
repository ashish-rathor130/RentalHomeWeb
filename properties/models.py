from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL


class Property(models.Model):
    host = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()
    price = models.IntegerField()
    location = models.CharField(max_length=200)
    image = models.ImageField(upload_to='property_images/')
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    

from datetime import timedelta
from django.utils.timezone import now

class Subscription(models.Model):
    PLAN_CHOICES = (
        ('free', 'Free'),
        ('recommended', 'Recommended'),
        ('pro', 'Pro'),
    )

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    plan = models.CharField(max_length=20, choices=PLAN_CHOICES, default='free')

    home_limit = models.IntegerField(default=5)
    start_date = models.DateTimeField(default=now)
    end_date = models.DateTimeField()

    def save(self, *args, **kwargs):
        # Set limits based on plan
        if self.plan == 'free':
            self.home_limit = 5
        elif self.plan == 'recommended':
            self.home_limit = 20
        elif self.plan == 'pro':
            self.home_limit = 9999  # unlimited

        # Set end date (1 month)
        self.end_date = self.start_date + timedelta(days=30)

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user} - {self.plan}"
