from django.contrib import admin
from .models import UserProfile

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'max_content_rating']
    list_filter = ['max_content_rating']
    search_fields = ['user__username']
