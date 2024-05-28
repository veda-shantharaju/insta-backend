from rest_framework import serializers
from posts.models import *
from users.serializers import CustomUserMiniSerializer

class PostListSerializer(serializers.ModelSerializer):
    user = CustomUserMiniSerializer()

    videos = serializers.SerializerMethodField()
    images = serializers.SerializerMethodField()
    like_count = serializers.SerializerMethodField()
    liked_by = serializers.SerializerMethodField()
    comment_count = serializers.SerializerMethodField()
    comments = serializers.SerializerMethodField()
    shared_count = serializers.SerializerMethodField()

    def get_videos(self, obj):
        videos = obj.video_set.all()
        return VideoSerializer(videos, many=True, context=self.context).data

    def get_images(self, obj):
        images = obj.image_set.all()
        return ImageSerializer(images, many=True, context=self.context).data

    def get_like_count(self, obj):
        return obj.postlike_set.count()

    def get_liked_by(self, obj):
        likes = obj.postlike_set.all()
        return CustomUserMiniSerializer([like.user for like in likes], many=True).data

    def get_comment_count(self, obj):
        return obj.comments.count()

    def get_comments(self, obj):
        comments = obj.comments.all()
        return CommentSerializer(comments, many=True).data

    def get_shared_count(self, obj):
        return obj.shared_posts.count()

    class Meta:
        model = Post
        fields = [
            'id',
            'user',
            'title',
            'description',
            'created_at',
            'updated_at',
            'is_archived',
            'videos',
            'images',
            'like_count',
            'liked_by',
            'comment_count',
            'comments',
            'shared_count'
        ]

class VideoSerializer(serializers.ModelSerializer):
    thumbnail1 = serializers.SerializerMethodField()

    def get_thumbnail1(self, obj):
        return obj.thumbnail1  # Assuming thumbnail1 is already a property in the Video model

    class Meta:
        model = Video
        fields = ('id', 'video_file', 'thumbnail1', 'uploaded_at')

class ImageSerializer(serializers.ModelSerializer):
    thumbnail2 = serializers.SerializerMethodField()

    def get_thumbnail2(self, obj):
        return obj.thumbnail2  # Assuming thumbnail2 is already a property in the Image model

    class Meta:
        model = Image
        fields = ('id', 'image_file', 'thumbnail2', 'uploaded_at')

class CommentSerializer(serializers.ModelSerializer):
    user = CustomUserMiniSerializer()

    class Meta:
        model = Comment
        fields = ('id', 'user', 'content', 'created_at', 'updated_at')

  # Add more fields as needed

class PostLikeSerializer(serializers.ModelSerializer):
    user = CustomUserMiniSerializer()

    class Meta:
        model = PostLike
        fields = ('id', 'user')

class SharedPostListSerializer(serializers.ModelSerializer):
    post = PostListSerializer()
    shared_by = CustomUserMiniSerializer()
    shared_with = CustomUserMiniSerializer(many=True)

    class Meta:
        model = SharedPost
        fields = ('id', 'post', 'shared_by', 'shared_with', 'shared_at')

class FollowRequestSerializer(serializers.ModelSerializer):
    from_user = serializers.ReadOnlyField(source='from_user.username')
    to_user = serializers.ReadOnlyField(source='to_user.username')

    class Meta:
        model = FollowRequest
        fields = ['id', 'from_user', 'to_user', 'created_at', 'accepted']

