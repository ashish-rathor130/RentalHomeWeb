# models.py
from django.db import models
from django.contrib.auth.models import User
from properties.models import Property
from django.conf import settings

# models.py
class Booking(models.Model):
    STATUS_CHOICES = (
        ('booked', 'Booked'),
        ('cancelled', 'Cancelled'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    property = models.ForeignKey(Property, on_delete=models.CASCADE)

    check_in = models.DateField()
    check_out = models.DateField()

    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='booked')

    booked_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.property.title} ({self.status})"