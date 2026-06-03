from django.contrib import admin
from .models import TransportRequest

@admin.register(TransportRequest)
class TransportRequestAdmin(admin.ModelAdmin):
    list_display    = ['pk', 'donor', 'facility', 'status', 'voucher_code', 'funding_source', 'created_at']
    list_filter     = ['status', 'funding_source']
    search_fields   = ['donor__user__first_name', 'donor__user__last_name', 'voucher_code']
    readonly_fields = ['voucher_code', 'created_at', 'updated_at']
