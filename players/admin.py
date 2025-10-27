from django.contrib import admin
from .models import Player


@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ('name', 'position', 'team', 'value')
    list_filter = ('position', 'team')
    search_fields = ('name', 'team__name')
