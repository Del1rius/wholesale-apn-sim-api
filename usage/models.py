from django.db import models
from inventory.models import SIMCard
from users.models import Organization
import uuid

# Represents a billing period for an organization.
# Used to track usage within specific time windows.
class BillingCycle(models.Model):
    cycle_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(
        Organization,
        on_delete = models.CASCADE,
        related_name = 'billing_cycles'
    )

    start_date = models.DateField()
    end_date = models.DateField()

    # Cycle metadata
    is_active = models.BooleanField(default=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-start_date']
        verbose_name = 'Billing Cycle'
        verbose_name_plural = 'Billing Cycles'
        unique_together = ['organization', 'start_date', 'end_date']

    def __str__(self):
        return f"{self.organization.name} - {self.start_date} to {self.end_date}"

# Individual data usage record for a SIM card.
# Created by Celery tasks that ingest usage data.
class DataUsageRecord(models.Model):
    record_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Relationships
    sim_card = models.ForeignKey(
        SIMCard,
        on_delete = models.CASCADE,
        related_name = 'usage_records'
    )

    billing_cycle = models.ForeignKey(
        BillingCycle,
        on_delete = models.CASCADE,
        related_name = 'usage_records',
        null = True,
        blank = True
    )

    # Usage Data
    data_consumed_mb = models.DecimalField(
        max_digits = 10,
        decimal_places = 2,
        help_text = "Data consumed in megabytes"
    )

    # Timestamps
    timestamp = models.DateTimeField(auto_now_add=True)
    recorded_at = models.DateTimeField(
        help_text = "When the usage actually occurred (may differ from timestamp)"
    )

    # Metadata
    source = models.CharField(
        max_length = 50,
        default = 'celery_task',
        help_text = "Source of the usage data (e.g., celery_task, manual_entry, api_import)"
    )

    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-recorded_at']
        verbose_name = 'Data Usage Record'
        verbose_name_plural = 'Data Usage Records'
        indexes = [
            models.Index(fields=['sim_card', '-recorded_at']),
            models.Index(fields=['billing_cycle', '-recorded_at']),
        ]

    def __str__(self):
        return f"{self.sim_card.iccid} - {self.data_consumed_mb}MB at {self.recorded_at}"