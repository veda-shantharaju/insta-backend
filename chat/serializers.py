from rest_framework import serializers
from chat.models import *
from users.serializers import CustomUserMiniSerializer

class MessageSerializer(serializers.ModelSerializer):
    sender = CustomUserMiniSerializer(read_only=True)

    class Meta:
        model = Message
        fields = ['id', 'chat', 'groupchat', 'sender', 'text', 'timestamp']
        read_only_fields = ['chat', 'groupchat']

class ChatSerializer(serializers.ModelSerializer):
    messages = MessageSerializer(many=True, read_only=True)

    class Meta:
        model = Chat
        fields = ['id', 'participants', 'messages', 'created_at']

class GroupChatSerializer(serializers.ModelSerializer):
    participants = CustomUserMiniSerializer(many=True, read_only=True)
    admins = CustomUserMiniSerializer(many=True, read_only=True)
    chats = ChatSerializer(many=True, read_only=True)
    created_by = CustomUserMiniSerializer( read_only=True)

    class Meta:
        model = GroupChat
        fields = ['id', 'name', 'participants', 'admins', 'created_by', 'chats', 'created_at']