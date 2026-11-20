from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .models import User
from .resources import UserResource
# Register your models here.
@admin.register(User)
class UserAdmin(ImportExportModelAdmin):
    resource_classes = [UserResource]
    list_display = ('id', 'username', 'email')