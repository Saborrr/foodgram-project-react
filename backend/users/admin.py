from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Follow, User


@admin.register(User)
class MyUserAdmin(UserAdmin):
    search_fields = ("username", "email", "first_name", "last_name",)
    list_filter = ("email", "first_name",)


admin.site.register(Follow)
