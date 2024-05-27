from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    ordering = ("id",)
    list_display = ('id', 'username', 'email', 'is_staff', 'is_superuser', 'is_active', 'is_private')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'is_private')
    search_fields = ('username', 'email', 'bio', 'location')

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email', 'bio', 'location', 'birth_date', 'contact_number', 'profile_picture','followers')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'is_private', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2'),
        }),
    )

admin.site.register(CustomUser, CustomUserAdmin)
