from django.contrib import admin
from .models import DonorProfile, EligibilityChecklist, DonationRecord


@admin.register(DonorProfile)
class DonorProfileAdmin(admin.ModelAdmin):
    list_display    = ['user', 'blood_type', 'status', 'district', 'needs_transport', 'created_at']
    list_filter     = ['blood_type', 'status', 'district', 'needs_transport']
    search_fields   = ['user__first_name', 'user__last_name', 'user__email', 'national_id']
    readonly_fields = ['created_at', 'updated_at']
    actions         = ['approve_donors', 'flag_donors']

    def approve_donors(self, request, queryset):
        queryset.update(status='approved')
    approve_donors.short_description = "Approve selected donors"

    def flag_donors(self, request, queryset):
        queryset.update(status='flagged')
    flag_donors.short_description = "Flag selected donors"


@admin.register(EligibilityChecklist)
class EligibilityChecklistAdmin(admin.ModelAdmin):
    list_display    = ['donor', 'is_auto_flagged', 'flagged_reason', 'completed_at']
    list_filter     = ['is_auto_flagged']
    readonly_fields = ['is_auto_flagged', 'flagged_reason', 'completed_at']


@admin.register(DonationRecord)
class DonationRecordAdmin(admin.ModelAdmin):
    list_display  = ['donor', 'facility', 'donated_at', 'blood_units', 'recorded_by']
    list_filter   = ['donated_at', 'facility']
    search_fields = ['donor__user__first_name', 'donor__user__last_name']
