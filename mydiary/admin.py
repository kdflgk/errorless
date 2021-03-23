from django.contrib import admin
from django.contrib.auth.models import User
from .models import Profile
from django.contrib.auth.admin import UserAdmin
from .models import Diary



# Register your models here.

admin.site.register(Diary)

class ProfileAdmin(admin.StackedInline):
    model = Profile
    con_delete = False


class CustomUserAdmin(UserAdmin):
    inlines = (ProfileAdmin,)

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)