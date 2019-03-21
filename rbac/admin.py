from django.contrib import admin

# Register your models here.

from rbac.models import *
# 自定义类，类名自己定，但必须继承ModelAdmin
class PermissionConfig(admin.ModelAdmin):
    list_display = ['pk', 'title', 'url']
    ordering = ['pk']  # 按照主键从低到高

admin.site.register(Permission, PermissionConfig)