from django.contrib import admin
from chat.models import *

# Register your models here.
class ChatAdmin(admin.ModelAdmin):
    list_display = [f.name for f in Chat._meta.fields]
    # date_hierarchy = "created_at"

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        # form.base_fields["user"].initial = request.user
        return form
    
class MessageAdmin(admin.ModelAdmin):
    search_fields = ["sender"]
    list_display = [f.name for f in Message._meta.fields]
    # date_hierarchy = "created_at"

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields["sender"].initial = request.user
        return form
    
class GroupChatAdmin(admin.ModelAdmin):
    search_fields = ["name"]
    list_display = [f.name for f in GroupChat._meta.fields]
    # date_hierarchy = "created_at"

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields["created_by"].initial = request.user
        return form

admin.site.register(Chat, ChatAdmin)
admin.site.register(Message, MessageAdmin)
admin.site.register(GroupChat, GroupChatAdmin)

