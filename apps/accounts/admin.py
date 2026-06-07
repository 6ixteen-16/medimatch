from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Facility


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display  = ['email', 'first_name', 'last_name', 'role', 'is_active', 'is_verified', 'facility']
    list_filter   = ['role', 'is_active', 'is_verified']
    search_fields = ['email', 'first_name', 'last_name']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = UserAdmin.fieldsets + (
        ('MediMatch', {'fields': ('role', 'phone_number', 'facility', 'is_verified')}),
    )


@admin.register(Facility)
class FacilityAdmin(admin.ModelAdmin):
    list_display  = ['name', 'facility_type', 'district', 'phone', 'is_active']
    list_filter   = ['facility_type', 'district', 'is_active']
    search_fields = ['name', 'district']
    readonly_fields = ['created_at', 'updated_at']
