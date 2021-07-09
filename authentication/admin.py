from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import *


class CustomUserAdmin(UserAdmin):
    list_display = UserAdmin.list_display+('sex','function', 'quality', 'role')
    fieldsets = UserAdmin.fieldsets + (
        ("Extra Fields", {'fields': (
            'sex', 'function', 'quality', 'role'
            )}),
    )


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(ConfirmToken)
