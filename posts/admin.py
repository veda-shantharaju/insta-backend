from django.contrib import admin
from posts.models import *

# Register your models here.
class VideoInline(admin.StackedInline):
    model = Video
    extra = 1
class ImageInline(admin.StackedInline):
    model = Image
    extra = 1
class PostAdmin(admin.ModelAdmin):
    search_fields = ["user"]
    list_display = [f.name for f in Post._meta.fields]
    date_hierarchy = "created_at"
    inlines=[VideoInline,ImageInline]

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields["user"].initial = request.user
        return form
    
class VideoAdmin(admin.ModelAdmin):
    # search_fields = ["user"]
    list_display = [f.name for f in Video._meta.fields]
    date_hierarchy = "uploaded_at"

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        # form.base_fields["user"].initial = request.user
        return form
    
class ImageAdmin(admin.ModelAdmin):
    # search_fields = ["user"]
    list_display = [f.name for f in Image._meta.fields]
    date_hierarchy = "uploaded_at"

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        # form.base_fields["user"].initial = request.user
        return form
    
class SharedPostAdmin(admin.ModelAdmin):
    search_fields = ["shared_by__username"]
    list_display = [f.name for f in SharedPost._meta.fields]
    # date_hierarchy = "created_at"

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields["shared_by"].initial = request.user
        return form
    
class FollowRequestAdmin(admin.ModelAdmin):
    search_fields = ["from_user"]
    list_display = [f.name for f in FollowRequest._meta.fields]
    # date_hierarchy = "created_at"

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields["from_user"].initial = request.user
        return form
    
class CommentAdmin(admin.ModelAdmin):
    search_fields = ["user"]
    list_display = [f.name for f in Comment._meta.fields]
    date_hierarchy = "created_at"

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields["user"].initial = request.user
        return form
    
class PostLikeAdmin(admin.ModelAdmin):
    search_fields = ["user"]
    list_display = [f.name for f in PostLike._meta.fields]
    # date_hierarchy = "created_at"

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields["user"].initial = request.user
        return form

    
admin.site.register(Post,PostAdmin)
admin.site.register(Video,VideoAdmin)
admin.site.register(Image,ImageAdmin)
admin.site.register(SharedPost,SharedPostAdmin)
admin.site.register(Comment,CommentAdmin)
admin.site.register(PostLike,PostLikeAdmin)
admin.site.register(FollowRequest,FollowRequestAdmin)
