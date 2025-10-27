from django.contrib import admin
from .models import TransferListing


@admin.register(TransferListing)
class TransferListingAdmin(admin.ModelAdmin):
    list_display = ('player', 'asking_price', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    readonly_fields = ('created_at', 'updated_at')
