from django.contrib import admin
from .models import APN, SIMCard


@admin.register(APN)
class APNAdmin(admin.ModelAdmin):
    list_display = ['name', 'apn_string', 'organization', 'authentication_type', 'is_active', 'date_created']
    list_filter = ['is_active', 'authentication_type', 'organization']
    search_fields = ['name', 'apn_string', 'organization__name']
    readonly_fields = ['apn_id', 'date_created', 'date_modified']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('apn_id', 'name', 'apn_string', 'is_active')
        }),
        ('Authentication', {
            'fields': ('authentication_type', 'username', 'password')
        }),
        ('Organization', {
            'fields': ('organization',)
        }),
        ('Timestamps', {
            'fields': ('date_created', 'date_modified'),
            'classes': ('collapse',)
        }),
    )


@admin.register(SIMCard)
class SIMCardAdmin(admin.ModelAdmin):
    list_display = ['iccid', 'phone_number', 'status', 'carrier', 'network_type', 'organization', 'date_created']
    list_filter = ['status', 'carrier', 'network_type', 'organization']
    search_fields = ['iccid', 'phone_number', 'carrier', 'organization__name']
    readonly_fields = ['sim_id', 'date_created', 'date_modified']
    
    fieldsets = (
        ('SIM Card Information', {
            'fields': ('sim_id', 'iccid', 'phone_number', 'status')
        }),
        ('Network Details', {
            'fields': ('carrier', 'network_type')
        }),
        ('Relationships', {
            'fields': ('organization', 'apn')
        }),
        ('Data Plan', {
            'fields': ('data_limit_mb', 'activation_date', 'expiry_date')
        }),
        ('Additional Information', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('date_created', 'date_modified'),
            'classes': ('collapse',)
        }),
    )
