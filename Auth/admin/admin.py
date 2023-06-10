from django.contrib import admin

from Auth.models import Module, Permission, User, UserRole

# Register your models here.
admin.site.register(UserRole)
admin.site.register(User)
admin.site.register(Module)
admin.site.register(Permission)
