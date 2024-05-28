import django_filters
from posts.models import *
from django.db.models import Q,Count
        
class PostFilter(django_filters.FilterSet):
    user_id =django_filters.CharFilter(field_name="user")
    is_archived = django_filters.BooleanFilter(field_name="is_archived",lookup_expr="icontains")
    followers_of_id = django_filters.NumberFilter(method='filter_followers_of')
    following_of_id = django_filters.NumberFilter(method='filter_following_of')
    like_count = django_filters.NumberFilter(method='filter_like_count')
    comment_count = django_filters.NumberFilter(method='filter_comment_count')
    shared_count = django_filters.NumberFilter(method='filter_shared_count')

    def filter_followers_of(self, queryset, name, value):
        """
        Filter posts where the user has followers.
        """
        return queryset.filter(user__followers__id=value)

    def filter_following_of(self, queryset, name, value):
        """
        Filter posts where the user is following.
        """
        return queryset.filter(Q(user__following__id=value) | Q(user_id=value))
    
    def filter_like_count(self, queryset, name, value):
        """
        Filter posts by the number of likes.
        """
        return queryset.annotate(like_count=Count('postlike')).filter(like_count=value)

    def filter_comment_count(self, queryset, name, value):
        """
        Filter posts by the number of comments.
        """
        return queryset.annotate(comment_count=Count('comments')).filter(comment_count=value)

    def filter_shared_count(self, queryset, name, value):
        """
        Filter posts by the number of shares.
        """
        return queryset.annotate(shared_count=Count('shared_posts')).filter(shared_count=value)

    class Meta:
        model = Post
        fields = ("id","user_id","is_archived",'followers_of_id',"following_of_id", 'like_count', 'comment_count', 'shared_count')

class VideoFilter(django_filters.FilterSet):
    class Meta:
        model = Video
        fields = ['post']

class ImageFilter(django_filters.FilterSet):
    class Meta:
        model = Image
        fields = ['post']

class SharedPostFilter(django_filters.FilterSet):
    class Meta:
        model = SharedPost
        fields = ['post', 'shared_by', 'shared_with', 'shared_at']

class CommentFilter(django_filters.FilterSet):
    class Meta:
        model = Comment
        fields = ['post', 'user', 'created_at', 'updated_at']

class PostLikeFilter(django_filters.FilterSet):
    class Meta:
        model = PostLike
        fields = ['post', 'user']

class FollowRequestFilter(django_filters.FilterSet):
    class Meta:
        model = FollowRequest
        fields = ['from_user', 'to_user', 'created_at', 'accepted']