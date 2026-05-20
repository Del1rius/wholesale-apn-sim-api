from django.db import models
from users.models import Organization
import uuid

# APN Configuration for data connectivity
class APN(models.Model):
    apn_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
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
    )

    is_active = models.BooleanField(default=True)
    date_created = models.DateTimeField(auto_now_add=True)
    data_modified = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-data_created']
        verbose_name = 'APN'
        verbose_name_plural = 'APNs'
    
    def __str__(self):
        return f"{self.name} - {self.apn_string}"

