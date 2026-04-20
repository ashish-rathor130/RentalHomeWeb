from django.contrib import admin
from .models import CustomUser, Profile, OTP

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email','phone','is_phone_verified', 'is_email_verified', 'is_host')
    search_fields = ('username', 'email', 'phone')
    list_filter = ('is_phone_verified', 'is_email_verified', 'is_host')
    
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'image')
    search_fields = ('user__username', 'user__email')   