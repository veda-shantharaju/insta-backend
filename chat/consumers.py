import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from chat.models import *
from django.utils import timezone
from posts.models import *
from users.models import *

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.chat_id = self.scope['url_route']['kwargs']['chat_id']
        self.chat_group_name = f'chat_{self.chat_id}'

        # Join room group
        await self.channel_layer.group_add(
            self.chat_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.chat_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        sender_id = text_data_json['sender_id']

        # Save message to database
        chat = await self.get_chat(self.chat_id)
        sender = await self.get_user(sender_id)
        await self.save_message(chat, sender, message)

        # Send message to room group
        await self.channel_layer.group_send(
            self.chat_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'sender_id': sender_id,
                'timestamp': timezone.now().isoformat()
            }
        )

    async def chat_message(self, event):
        message = event['message']
        sender_id = event['sender_id']
        timestamp = event['timestamp']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'sender_id': sender_id,
            'timestamp': timestamp
        }))

    @database_sync_to_async
    def get_chat(self, chat_id):
        return Chat.objects.get(id=chat_id)

    @database_sync_to_async
    def get_user(self, user_id):
        return CustomUser.objects.get(id=user_id)

    @database_sync_to_async
    def save_message(self, chat, sender, message):
        return Message.objects.create(chat=chat, sender=sender, text=message)


class GroupChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.groupchat_id = self.scope['url_route']['kwargs']['groupchat_id']
        self.groupchat_group_name = f'groupchat_{self.groupchat_id}'

        # Join room group
        await self.channel_layer.group_add(
            self.groupchat_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.groupchat_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        sender_id = text_data_json['sender_id']

        # Save message to database
        groupchat = await self.get_groupchat(self.groupchat_id)
        sender = await self.get_user(sender_id)
        await self.save_message(groupchat, sender, message)

        # Send message to room group
        await self.channel_layer.group_send(
            self.groupchat_group_name,
            {
                'type': 'groupchat_message',
                'message': message,
                'sender_id': sender_id,
                'timestamp': timezone.now().isoformat()
            }
        )

    async def groupchat_message(self, event):
        message = event['message']
        sender_id = event['sender_id']
        timestamp = event['timestamp']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'sender_id': sender_id,
            'timestamp': timestamp
        }))

    @database_sync_to_async
    def get_groupchat(self, groupchat_id):
        return GroupChat.objects.get(id=groupchat_id)

    @database_sync_to_async
    def get_user(self, user_id):
        return CustomUser.objects.get(id=user_id)

    @database_sync_to_async
    def save_message(self, groupchat, sender, message):
        return Message.objects.create(groupchat=groupchat, sender=sender, text=message)


class CommentConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.post_id = self.scope['url_route']['kwargs']['post_id']
        self.comment_group_name = f'comment_{self.post_id}'

        # Join room group
        await self.channel_layer.group_add(
            self.comment_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.comment_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        comment = text_data_json['comment']
        sender_id = text_data_json['sender_id']

        # Save comment to database
        post = await self.get_post(self.post_id)
        sender = await self.get_user(sender_id)
        await self.save_comment(post, sender, comment)

        # Send comment to room group
        await self.channel_layer.group_send(
            self.comment_group_name,
            {
                'type': 'comment_message',
                'comment': comment,
                'sender_id': sender_id,
                'timestamp': timezone.now().isoformat()
            }
        )

    async def comment_message(self, event):
        comment = event['comment']
        sender_id = event['sender_id']
        timestamp = event['timestamp']

        # Send comment to WebSocket
        await self.send(text_data=json.dumps({
            'comment': comment,
            'sender_id': sender_id,
            'timestamp': timestamp
        }))

    @database_sync_to_async
    def get_post(self, post_id):
        return Post.objects.get(id=post_id)

    @database_sync_to_async
    def get_user(self, user_id):
        return CustomUser.objects.get(id=user_id)

    @database_sync_to_async
    def save_comment(self, post, sender, comment):
        return Comment.objects.create(post=post, user=sender, content=comment)
