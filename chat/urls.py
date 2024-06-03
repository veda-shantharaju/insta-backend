from django.urls import path
from .views import *

urlpatterns = [
    path('chats/', ChatListCreateView.as_view(), name='chat-list-create'),
    path('chats/<int:chat_id>/messages/', MessageListCreateView.as_view(), name='message-list-create'),
    path('chats/messages/<int:chat_id>/', ContinuousMessageListView.as_view(), name='continuous-message-list'),

    path('group-chats/', GroupChatListCreateView.as_view(), name='group-chat-list-create'),
    path('group-chats/<int:group_chat_id>/messages-hist/', GroupChatMessageListView.as_view(), name='group-chat-detail'),
    path('group-chats/<int:group_chat_id>/messages/', GroupChatMessageListCreateView.as_view(), name='group-chat-message-list-create'),
    path('group-chats/admins/', GroupChatAdminListView.as_view(), name='group-chat-admin-list'),
    path('group-chats/admins/add/', GroupChatAdminUpdateView.as_view(), name='group-chat-admin-add'),
    path('group-chats/admins/remove/', GroupChatAdminRemoveView.as_view(), name='group-chat-admin-remove'),
]
