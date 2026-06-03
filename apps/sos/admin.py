from django.contrib import admin
from .models import SOSRequest, SOSStatusUpdate


@admin.register(SOSRequest)
class SOSRequestAdmin(admin.ModelAdmin):
    list_display    = ['pk', 'requesting_facility', 'blood_type_needed', 'units_needed', 'urgency', 'status', 'is_overdue', 'created_at']
    list_filter     = ['status', 'urgency', 'blood_type_needed', 'is_overdue']
    search_fields   = ['requesting_facility__name', 'target_bank__name']
    readonly_fields = ['created_at', 'updated_at', 'deadline', 'resolved_at']


@admin.register(SOSStatusUpdate)
class SOSStatusUpdateAdmin(admin.ModelAdmin):
    list_display  = ['sos_request', 'old_status', 'new_status', 'updated_by', 'updated_at']
    readonly_fields = ['updated_at']
