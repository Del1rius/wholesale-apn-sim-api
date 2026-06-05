from django.contrib import admin
from usage.models import BillingCycle, DataUsageRecord

# Admin interface for BillingCycle model
@admin.register(BillingCycle)
class BillingCycleAdmin(admin.ModelAdmin):
    list_display = [
        'cycle_id',
        'organization',
        'start_date',
        'end_date',
        'is_active',
        'date_created'
    ]

    list_filter = [
        'is_active',
        'organization',
        'start_date',
        'end_date'
    ]

    search_fields = [
        'organization__name',
        'cycle_id'
    ]

    readonly_fields = [
        'cycle_id',
        'date_created',
        'date_modified'
    ]

    fieldsets = (
        ('Billing Cycle Information', {
            'fields': ('cycle_id', 'organization', 'start_date', 'end_date', 'is_active')
        }),
        ('Metadata', {
            'fields': ('date_created', 'date_modified'),
            'classes': ('collapse',)
        })
    )

    ordering = ['-start_date']
    date_hierarchy = 'start_date'

# Admin interface for DataUsageRecord model
@admin.register(DataUsageRecord)
class DataUsageRecordAdmin(admin.ModelAdmin):
    list_display = [
        'record_id',
        'sim_card_iccid',
        'data_consumed_mb',
        'recorded_at',
        'billing_cycle',
        'source',
        'timestamp'
    ]

    list_filter = [
        'source',
        'recorded_at',
        'billing_cycle',
        'sim_card__status',
        'sim_card__organization'
    ]

    search_fields = [
        'record_id',
        'sim_card__iccid',
        'sim_card__phone_number',
        'notes'
    ]

    readonly_fields = [
        'record_id',
        'timestamp'
    ]

    fieldsets = (
        ('Usage Record Information', {
            'fields': ('record_id', 'sim_card', 'billing_cycle', 'data_consumed_mb', 'recorded_at')
        }),
        ('Source & Metadata', {
            'fields': ('source', 'notes', 'timestamp')
        })
    )

    ordering = ['-recorded_at']
    date_hierarchy = 'recorded_at'

    def sim_card_iccid(self, obj):
        # Display SIM card ICCID in list view
        return obj.sim_card.iccid
    sim_card_iccid.short_description = 'SIM ICCID'
    sim_card_iccid.admin_order_field = 'sim_card__iccid'
