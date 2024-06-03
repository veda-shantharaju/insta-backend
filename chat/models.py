from django.db import models
from users.models import CustomUser

# Create your models here.
class Chat(models.Model):
    participants = models.ManyToManyField(CustomUser, related_name='chats')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Chat {self.id}"

class GroupChat(models.Model):
    name = models.CharField(max_length=100)
    participants = models.ManyToManyField(CustomUser, related_name='group_chats')
    admins = models.ManyToManyField(CustomUser, related_name='admin_group_chats', blank=True)
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='created_group_chats', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    
class Message(models.Model):
    chat = models.ForeignKey(Chat, related_name='messages', on_delete=models.CASCADE,blank=True, null=True)
    groupchat = models.ForeignKey(GroupChat, related_name='groupmessages', on_delete=models.CASCADE,blank=True, null=True)
    sender = models.ForeignKey(CustomUser, related_name='sender', on_delete=models.CASCADE)
    text = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message {self.id} from {self.sender.username}"