"""
Django admin customization.
"""

from django.contrib import admin  # noqa
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
# Import the gettext_lazy function as '_' for marking strings as translatable in Django  # noqa
from django.utils.translation import gettext_lazy as _

from core import models

class UserAdmin(BaseUserAdmin):
    """Define the admin pages for users."""
    ordering = ['id']
    list_display = ['email', 'name']
    fieldsets = (
        (None, {'fields': ('email', 'password')}), # None for title  # noqa
        (
            _('Permissions'),
            {
                'fields': (
                    'is_active',
                    'is_staff',
                    'is_superuser'
                )
            }
        ),
        (
            _('Important dates'),
            {'fields': ('last_login',)}
        ),
    )
    readonly_fields = ['last_login']
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields':(
                'email',
                'password1',
                'password2',
                'name',
                'is_active',
                'is_staff',
                'is_superuser',
            )
        }),
    )


admin.site.register(models.User, UserAdmin)