from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from users.models import Organization
import uuid

# APN Configuration for data connectivity


class APN(models.Model):
    apn_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    apn_string = models.CharField(max_length=255)
    username = models.CharField(max_length=100, blank=True, null=True)
    password = models.CharField(max_length=100, blank=True, null=True)
    authentication_type = models.CharField(
        max_length=20,
        choices=[
            ('none', 'None'),
            ('pap', 'PAP'),
            ('chap', 'CHAP'),
            ('pap_chap', 'PAP or CHAP')
        ],
        default='none'
    )

    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='apns',
        null=True,
        blank=True
    )  # If null, it's a shared/public apn

    is_active = models.BooleanField(default=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date_created']
        verbose_name = 'APN'
        verbose_name_plural = 'APNs'

    def __str__(self):
        return f"{self.name} - {self.apn_string}"

# SIM Card Inventory Management


class SIMCard(models.Model):
    sim_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False)
    # Integrated Circuit Card ID
    iccid = models.CharField(max_length=22, unique=True)
    phone_number = models.CharField(
        max_length=20, unique=True, null=True, blank=True)

    STATUS_CHOICES = [
        ('available', 'Available'),
        ('assigned', 'Assigned'),
        ('suspended', 'Suspended'),
        ('deactivated', 'Deactivated'),
        ('lost', 'Lost/Stolen')
    ]

    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='available')

    # Network Information
    carrier = models.CharField(max_length=100)
    network_type = models.CharField(
        max_length=10,
        choices=[
            ('2G', '2G'),
            ('3G', '3G'),
            ('4G', '4G/LTE'),
            ('5G', '5G')
        ],
        default='4G'
    )

    # Relationships
    organization = models.ForeignKey(
        Organization,
        on_delete=models.SET_NULL,
        related_name='sim_cards',
        null=True,
        blank=True
    )  # Which Organization owns/uses this SIM

    apn = models.ForeignKey(
        APN,
        on_delete=models.SET_NULL,
        related_name='sim_cards',
        null=True,
        blank=True
    )  # Which APN configuration is assigned

    # Data plan information
    data_limit_mb = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(100000)],
        help_text="Monthly data limit in MB (maximum 100,000 MB)"
    )  # Monthly data limit in MB

    # Metadata
    activation_date = models.DateField(null=True, blank=True)
    expiry_date = models.DateField(null=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-date_created']
        verbose_name = 'SIM Card'
        verbose_name_plural = 'SIM Cards'

    def __str__(self):
        return f"{self.iccid} - {self.phone_number or 'No Number'} ({self.status})"
