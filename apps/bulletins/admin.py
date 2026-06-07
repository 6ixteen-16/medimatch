from django.contrib import admin
from .models import Bulletin

@admin.register(Bulletin)
class BulletinAdmin(admin.ModelAdmin):
    list_display    = ['title', 'category', 'facility', 'status', 'sms_sent', 'event_date', 'created_at']
    list_filter     = ['category', 'status', 'sms_sent']
    search_fields   = ['title', 'facility__name']
    readonly_fields = ['sms_sent_at', 'created_at', 'updated_at']
    actions         = ['publish_bulletins']

    def publish_bulletins(self, request, queryset):
        queryset.update(status='published')
    publish_bulletins.short_description = "Publish selected bulletins"
