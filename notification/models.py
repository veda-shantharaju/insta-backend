from django.db import models
from users.models import CustomUser
from chat.models import *
from posts.models import *

class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ('message', 'Message'),
        ('comment', 'Comment'),
        ('post_like', 'Post Like'),
        ('follow_request', 'Follow Request'),
    )

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='notifications')
    from_user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='sent_notifications', null=True, blank=True)
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='notifications', null=True, blank=True)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='notifications', null=True, blank=True)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='notifications', null=True, blank=True)
    follow_request = models.ForeignKey(FollowRequest, on_delete=models.CASCADE, related_name='notifications', null=True, blank=True)
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username}: {self.get_notification_type_display()}"

    class Meta:
        ordering = ['-created_at']