from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models

class CustomUser(AbstractUser):
    is_ops_user = models.BooleanField(default=False)
    is_client_user = models.BooleanField(default=False)

# Define related_name for groups and user_permissions
CustomUser._meta.get_field('groups').remote_field.related_name = 'custom_user_groups'
CustomUser._meta.get_field('user_permissions').remote_field.related_name = 'custom_user_permissions'

class File(models.Model):
    uploaded_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    file = models.FileField(upload_to='uploads/')
    upload_time = models.DateTimeField(auto_now_add=True)
