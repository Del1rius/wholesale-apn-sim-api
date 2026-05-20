from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid

# Represents enterprise clients (multi-tenancy
class Organization(models.Model):
    org_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    industry = models.CharField(max_length=255, blank=True)
    contact_email = models.EmailField(unique=True)
    date_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'organizations'
        verbose_name_plural = 'Organizations'

    def __str__(self):
        return self.name

#Custom user model with organization and role
class User(AbstractUser):
    ROLE_CHOICES = [
        ('network_admin', 'Network Administator'),
        ('client_manager', 'Client Manager'),
    ]

    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='users'
    )

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='client_manager')
    phone_number = models.CharField(max_length=20, blank=True)

    class Meta:
        db_table = 'users'

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"