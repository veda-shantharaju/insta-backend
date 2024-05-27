from django.urls import path
from posts.views import *

urlpatterns = [
    path('posts/', PostCreateAPIView.as_view(), name='post-create'),
    path('postlist/', PostListAPIView.as_view(), name='post-list'),
    path('postdelete/<int:pk>/', PostDelete.as_view(), name='post-delete'),
    path('follow/request/', FollowRequestCreateAPIView.as_view(), name='follow-request'),
    path('follow/response/', FollowRequestResponseAPIView.as_view(), name='follow-response'),
    path('posts-update/', PostUpdateAPIView.as_view(), name='post-update'),
    path('share/', SharePostView.as_view(), name='share-post'),
    path('comment/', CommentCreateView.as_view(), name='create-comment'),
    path('comment/<int:pk>/', CommentDeleteView.as_view(), name='delete-comment'),
    path('like/', PostLikeView.as_view(), name='like-unlike-post'),
]
