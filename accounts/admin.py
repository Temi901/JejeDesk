from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Business, User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (("JejeDesk", {"fields": ("business", "role")}),)
    list_display = ("username", "email", "business", "role")


admin.site.register(Business)