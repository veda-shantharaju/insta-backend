from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from chat.models import *
from chat.serializers import *
from users.models import CustomUser
from rest_framework.views import APIView
from django.db.models import Q


class ChatListCreateView(generics.ListCreateAPIView):
    serializer_class = ChatSerializer
    permission_classes = [permissions.IsAuthenticated]
    def get_queryset(self):
        return Chat.objects.filter(participants=self.request.user)
    def perform_create(self, serializer):
        chat = serializer.save()
        chat.participants.add(self.request.user)

class MessageListCreateView(generics.ListCreateAPIView):
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]
    def get_queryset(self):
        chat_id = self.kwargs['chat_id']
        return Message.objects.filter(chat__id=chat_id)
    def perform_create(self, serializer):
        chat_id = self.kwargs['chat_id']
        chat = get_object_or_404(Chat, id=chat_id)
        if self.request.user not in chat.participants.all():
            return Response({"detail": "You are not a participant of this chat."}, status=status.HTTP_403_FORBIDDEN)
        serializer.save(chat=chat, sender=self.request.user)

class ContinuousMessageListView(generics.ListAPIView):
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]
    def get_queryset(self):
        chat_id = self.kwargs['chat_id']
        chat = get_object_or_404(Chat, id=chat_id)
        if self.request.user not in chat.participants.all():
            return Response({"detail": "You are not a participant of this chat."}, status=status.HTTP_403_FORBIDDEN)
        return Message.objects.filter(chat=chat).order_by('timestamp')
    
class GroupChatListCreateView(generics.ListCreateAPIView):
    queryset = GroupChat.objects.all()
    serializer_class = GroupChatSerializer
    permission_classes = [permissions.IsAuthenticated]
    def create(self, request, *args, **kwargs):
        participant_ids = request.data.get('participants', [])
        if isinstance(participant_ids, str):
            participant_ids = list(map(int, participant_ids.split(',')))
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        group_chat = serializer.save(created_by=request.user)
        group_chat.admins.add(request.user)
        if participant_ids:
            participants = CustomUser.objects.filter(id__in=participant_ids)
            group_chat.participants.set(participants)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

class GroupChatMessageListView(generics.ListAPIView):
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]
    def get_queryset(self):
        group_chat_id = self.kwargs['group_chat_id']
        group_chat = get_object_or_404(GroupChat, id=group_chat_id)
        # Fetch all messages related to the group chat through the `group_chat` foreign key in `Chat`
        messages = Message.objects.filter(groupchat=group_chat).order_by('timestamp')
        return messages

class GroupChatMessageListCreateView(generics.ListCreateAPIView):
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]
    def get_queryset(self):
        group_chat_id = self.kwargs['group_chat_id']
        group_chat = get_object_or_404(GroupChat, id=group_chat_id)
        if self.request.user not in group_chat.participants.all():
            return Message.objects.none()  # Return an empty queryset if the user is not a participant
        return Message.objects.filter(groupchat=group_chat).order_by('timestamp')
    def perform_create(self, serializer):
        group_chat_id = self.kwargs['group_chat_id']
        group_chat = get_object_or_404(GroupChat, id=group_chat_id)
        if self.request.user not in group_chat.participants.all():
            raise serializers.ValidationError({"detail": "You are not a participant of this group chat."})
        # Create a Chat instance for this GroupChat if it doesn't already exist
        chat, created = Chat.objects.get_or_create(
            id=group_chat.id, defaults={'created_at': group_chat.created_at}
        )
        chat.participants.set(group_chat.participants.all())
        serializer.save(chat=chat, groupchat=group_chat, sender=self.request.user)

class GroupChatAdminListView(generics.ListAPIView):
    serializer_class = GroupChatSerializer
    permission_classes = [permissions.IsAuthenticated]
    def get_queryset(self):
        return GroupChat.objects.filter(participants=self.request.user.id)

class GroupChatAdminUpdateView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def post(self, request, *args, **kwargs):
        groupchat_id = request.data.get('groupchat_id')
        user_id = request.data.get('user_id')
        try:
            group_chat = GroupChat.objects.get(id=groupchat_id)
        except GroupChat.DoesNotExist:
            return Response({"detail": "Group chat does not exist."}, status=404)
        if not user_id:
            return Response({"detail": "User ID is required."}, status=400)
        if group_chat.admins.filter(id__in=user_id).exists():
            return Response({"detail": "User is already an admin of this group chat."})
        user = CustomUser.objects.get(id__in=user_id)
        group_chat.admins.add(user)
        group_chat.save()
        return Response({"detail": f"User is now an admin of group chat {group_chat.name}."})

class GroupChatAdminRemoveView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def post(self, request, *args, **kwargs):
        groupchat_id = request.data.get('groupchat_id')
        user_id = request.data.get('user_id')
        try:
            group_chat = GroupChat.objects.get(id=groupchat_id)
        except GroupChat.DoesNotExist:
            return Response({"detail": "Group chat does not exist."}, status=404)
        if not user_id:
            return Response({"detail": "User ID is required."}, status=400)
        try:
            user = CustomUser.objects.get(id=user_id)
        except CustomUser.DoesNotExist:
            return Response({"detail": "User does not exist."}, status=404)
        if not group_chat.admins.filter(id=user_id).exists():
            return Response({"detail": "User is not an admin of this group chat to remove."})
        group_chat.admins.remove(user)
        group_chat.save()
        return Response({"detail": f"User {user.username} is no longer an admin of group chat {group_chat.name}."})