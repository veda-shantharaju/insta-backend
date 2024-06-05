from django.contrib import admin
from notification.models import *

# Register your models here.
class NotificationAdmin(admin.ModelAdmin):
    search_fields = ["user"]
    list_display = [f.name for f in Notification._meta.fields]
    date_hierarchy = "created_at"

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields["user"].initial = request.user
        return form
    
admin.site.register(Notification,NotificationAdmin)