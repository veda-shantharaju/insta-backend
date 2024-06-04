from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/chat/(?P<chat_id>\w+)/$', consumers.ChatConsumer.as_asgi()),
    re_path(r'ws/groupchat/(?P<groupchat_id>\w+)/$', consumers.GroupChatConsumer.as_asgi()),
    re_path(r'ws/comment/(?P<post_id>\w+)/$', consumers.CommentConsumer.as_asgi()),
]
