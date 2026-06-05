from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Organization


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ['name', 'industry', 'contact_email', 'date_created']
    search_fields = ['name', 'industry', 'contact_email']
    readonly_fields = ['org_id', 'date_created']

    fieldsets = (
        ('Organization Information', {
            'fields': ('org_id', 'name', 'industry', 'contact_email')
        }),
        ('Timestamps', {
            'fields': ('date_created',),
            'classes': ('collapse',)
        }),
    )


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    # Fields to display in the user list
    list_display = ['username', 'email', 'first_name', 'last_name', 'role', 'organization', 'is_staff']
    list_filter = ['role', 'organization', 'is_staff', 'is_superuser', 'is_active']
    search_fields = ['username', 'email', 'first_name', 'last_name', 'phone_number']

    # Customize the user edit form
    fieldsets = (
        (None, {
            'fields': ('username', 'password')
        }),
        ('Personal Info', {
            'fields': ('first_name', 'last_name', 'email', 'phone_number')
        }),
        ('Organization & Role', {
            'fields': ('organization', 'role')
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
            'classes': ('collapse',)
        }),
        ('Important Dates', {
            'fields': ('last_login', 'date_joined'),
            'classes': ('collapse',)
        }),
    )

    # Customize the add user form
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'organization', 'role', 'phone_number'),
        }),
    )
