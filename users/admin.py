from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from users.models import *

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

class PasswordResetOTPAdmin(admin.ModelAdmin):
    search_fields = ["user"]
    list_display = [f.name for f in PasswordResetOTP._meta.fields]
    # date_hierarchy = "created_at"

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields["user"].initial = request.user
        return form

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(PasswordResetOTP, PasswordResetOTPAdmin)

