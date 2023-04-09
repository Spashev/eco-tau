from django.contrib import admin
from account.models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'email', 'username', 'is_active')
    list_display_links = ('id', 'email', 'username')
    list_filter = ('is_active', 'is_superuser')
    search_fields = ('id', 'email', 'username')

