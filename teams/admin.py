from django.contrib import admin
from .models import Team


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'capital')
    search_fields = ('name', 'user__username')
    readonly_fields = ('capital',)
