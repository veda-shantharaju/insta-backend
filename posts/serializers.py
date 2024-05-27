from rest_framework import serializers
from posts.models import *
from users.serializers import CustomUserMiniSerializer

class PostListSerializer(serializers.ModelSerializer):

    user = serializers.SerializerMethodField()
    def get_user(self, obj):
        return CustomUserMiniSerializer(obj.user,context= self.context).data
    
    videos = serializers.SerializerMethodField()
    def get_videos(self, obj):
        return VideoSerializer(obj.video_set.all(),many=True,context= self.context).data
    
    images = serializers.SerializerMethodField()
    def get_images(self, obj):
        return ImageSerializer(obj.image_set.all(),many=True,context= self.context).data
    class Meta:
        model = Post
        fields = [
            'id',
            'user', 
            'title', 
            'description',
            "created_at",
            "updated_at",
            "is_archived",
            "videos",
            "images"
            ]
        
class VideoSerializer(serializers.ModelSerializer):

    thumbnail1=serializers.SerializerMethodField()
    def get_thumbnail1(self, obj):
        if obj.video_file:
            return self.context.get("request").build_absolute_uri(obj.thumbnail1)
        
    class Meta:
        model = Video
        fields = ("id","post","video_file",'thumbnail1',"uploaded_at")

class ImageSerializer(serializers.ModelSerializer):

    thumbnail2=serializers.SerializerMethodField()
    def get_thumbnail2(self, obj):
        if obj.image_file:
            return self.context.get("request").build_absolute_uri(obj.thumbnail2)
        
    class Meta:
        model = Image
        fields = ("id","post", "image_file","thumbnail2","uploaded_at")

class SharedPostListSerializer(serializers.ModelSerializer):

    post = serializers.SerializerMethodField()
    def get_post(self, obj):
        return PostListSerializer(obj.post,context= self.context).data
    
    shared_by = serializers.SerializerMethodField()
    def get_shared_by(self, obj):
        return CustomUserMiniSerializer(obj.shared_by,context= self.context).data
    
    shared_with = serializers.SerializerMethodField()
    def get_shared_with(self, obj):
        return CustomUserMiniSerializer(obj.shared_with,context= self.context).data
    
    class Meta:
        model = SharedPost
        fields = ("id", 
                  "post",
                  "shared_by",
                  "shared_with",
                  "shared_at")
        
class CommentSerializer(serializers.ModelSerializer):

    post = serializers.SerializerMethodField()
    def get_post(self, obj):
        return PostListSerializer(obj.post,context= self.context).data
    
    user = serializers.SerializerMethodField()
    def get_user(self, obj):
        return CustomUserMiniSerializer(obj.user,context= self.context).data
    
    class Meta:
        model = Comment
        fields = ("id", "post","user","content","created_at","updated_at")

class PostLikeSerializer(serializers.ModelSerializer):

    post = serializers.SerializerMethodField()
    def get_post(self, obj):
        return PostListSerializer(obj.post,context= self.context).data
    
    user = serializers.SerializerMethodField()
    def get_user(self, obj):
        return CustomUserMiniSerializer(obj.user,context= self.context).data
    
    class Meta:
        model = PostLike
        fields = ("id", "post","user")

class UserFollowSerializer(serializers.ModelSerializer):

    follower = serializers.SerializerMethodField()
    def get_follower(self, obj):
        return CustomUserMiniSerializer(obj.follower,context= self.context).data
    
    following = serializers.SerializerMethodField()
    def get_following(self, obj):
        return CustomUserMiniSerializer(obj.following,context= self.context).data
    
    class Meta:
        model = UserFollow
        fields = ("id", "follower","following")

class FollowRequestSerializer(serializers.ModelSerializer):
    from_user = serializers.ReadOnlyField(source='from_user.username')
    to_user = serializers.ReadOnlyField(source='to_user.username')

    class Meta:
        model = FollowRequest
        fields = ['id', 'from_user', 'to_user', 'created_at', 'accepted']

