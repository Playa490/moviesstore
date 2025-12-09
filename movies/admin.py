from django.contrib import admin
from .models import Movie, Review

class MovieAdmin(admin.ModelAdmin):
    ordering = ['name']
    search_fields = ['name']
    list_display = ['name', 'rating', 'price']
    list_filter = ['rating']

admin.site.register(Movie, MovieAdmin)
admin.site.register(Review)