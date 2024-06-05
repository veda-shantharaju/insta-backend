import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from chat.models import *
from django.utils import timezone
from posts.models import *
from users.models import *
from notification.models import Notification
from asgiref.sync import sync_to_async

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        try:
            self.chat_id = self.scope['url_route']['kwargs']['chat_id']
        except KeyError:
            self.chat_id = None

        if self.chat_id:
            self.chat_group_name = f'chat_{self.chat_id}'

            # Join room group
            await self.channel_layer.group_add(
                self.chat_group_name,
                self.channel_name
            )
            await self.accept()
        else:
            await self.close()

    async def disconnect(self, close_code):
        if self.chat_id:
            # Leave room group
            await self.channel_layer.group_discard(
                self.chat_group_name,
                self.channel_name
            )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_text = text_data_json['message']
        sender_id = text_data_json['sender_id']

        # Save message to database
        chat = await self.get_chat(self.chat_id)
        sender = await self.get_user(sender_id)
        message = await self.save_message(chat, sender, message_text)

        # Send message to room group
        await self.channel_layer.group_send(
            self.chat_group_name,
            {
                'type': 'chat_message',
                'message': message.text,  # Sending text as part of the message
                'sender_id': sender_id,
                'timestamp': timezone.now().isoformat()
            }
        )

        # Create notification
        await self.create_notification(sender, 'message', message, chat)

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

    @database_sync_to_async
    def create_notification(self, from_user, notification_type, message, chat):
        user = chat.participants.exclude(id=from_user.id).first()  # Assuming participants is the related name for users in Chat
        if user:
            Notification.objects.create(
                user=user,
                from_user=from_user,
                message=message,  # Ensure `message` is a Message instance
                notification_type=notification_type,
                title=f"New {notification_type.capitalize()}",
                description=f"You have a new {notification_type} from {from_user.username}"
            )
        else:
            print(f"No participant found for chat with id {chat.id}")


class GroupChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        try:
            self.groupchat_id = self.scope['url_route']['kwargs']['groupchat_id']
        except KeyError:
            self.groupchat_id = None

        if self.groupchat_id:
            self.groupchat_group_name = f'groupchat_{self.groupchat_id}'

            # Join room group
            await self.channel_layer.group_add(
                self.groupchat_group_name,
                self.channel_name
            )
            await self.accept()
        else:
            await self.close()

    async def disconnect(self, close_code):
        if self.groupchat_id:
            # Leave room group
            await self.channel_layer.group_discard(
                self.groupchat_group_name,
                self.channel_name
            )

    async def receive(self, text_data):
        if self.groupchat_id:
            text_data_json = json.loads(text_data)
            message_text = text_data_json['message']
            sender_id = text_data_json['sender_id']

            # Save message to database
            groupchat = await self.get_groupchat(self.groupchat_id)
            sender = await self.get_user(sender_id)
            message = await self.save_message(groupchat, sender, message_text)

            # Create notification
            await self.create_notification(groupchat, sender, message, 'message')

            # Send message to room group
            await self.channel_layer.group_send(
                self.groupchat_group_name,
                {
                    'type': 'groupchat_message',
                    'message': message_text,
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

    @database_sync_to_async
    def create_notification(self, groupchat, sender, message, notification_type):
        participants = groupchat.participants.exclude(id=sender.id)
        message_instance = Message.objects.get(id=message.id)  # Fetch the Message instance

        for participant in participants:
            Notification.objects.create(
                user=participant,
                from_user=sender,
                message=message_instance,
                notification_type=notification_type,
                title=f"New {notification_type.capitalize()}",
                description=f"You have a new {notification_type} from {sender.username}"
            )
        else:
            print(f"No participant found for groupchat with id {groupchat.id}")

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
        comment_content = text_data_json['comment']
        sender_id = text_data_json['sender_id']

        # Save comment to database
        post = await self.get_post(self.post_id)
        sender = await self.get_user(sender_id)
        comment = await self.save_comment(post, sender, comment_content)

        # Create notification
        await self.create_notification(post, sender, comment, 'comment')

        # Send comment to room group
        await self.channel_layer.group_send(
            self.comment_group_name,
            {
                'type': 'comment_message',
                'comment': comment.content,
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

    @sync_to_async
    def get_post(self, post_id):
        return Post.objects.get(id=post_id)

    @sync_to_async
    def get_user(self, user_id):
        return CustomUser.objects.get(id=user_id)

    @sync_to_async
    def save_comment(self, post, sender, comment_content):
        return Comment.objects.create(post=post, user=sender, content=comment_content)

    @database_sync_to_async
    def create_notification(self, post, sender, comment, notification_type):
        Notification.objects.create(
            user=post.user,
            from_user=sender,
            comment=comment,
            notification_type=notification_type,
            title=f"New {notification_type.capitalize()}",
            description=f"You have a new {notification_type} from {sender.username}"
        )