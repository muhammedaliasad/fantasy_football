from django.contrib import admin
from .models import Transaction


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('player', 'seller', 'buyer', 'transfer_amount', 'created_at')
    list_filter = ('created_at', 'is_active')
    readonly_fields = ('created_at',)
