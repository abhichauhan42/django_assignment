from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import CustomUser, File

class CustomUserAdmin(BaseUserAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'is_ops_user', 'is_client_user')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'is_ops_user', 'is_client_user')}
        ),
    )
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_ops_user', 'is_client_user')
    list_filter = ('is_staff', 'is_superuser', 'is_ops_user', 'is_client_user')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    ordering = ('username',)

class FileAdmin(admin.ModelAdmin):
    list_display = ('uploaded_by', 'file', 'upload_time')
    list_filter = ('uploaded_by', 'upload_time')
    search_fields = ('uploaded_by__username', 'file')

# Unregister the original User admin
admin.site.unregister(User)

# Register the new CustomUser admin
admin.site.register(CustomUser, CustomUserAdmin)

# Register the File admin
admin.site.register(File, FileAdmin)
