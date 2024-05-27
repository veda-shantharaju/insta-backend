from django.db import models
from users.models import CustomUser
from sorl.thumbnail import get_thumbnail

class Post(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    title = models.CharField(max_length=32, blank=True, null=True)
    description = models.CharField(max_length=164, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_archived = models.BooleanField(default=False)

    def __str__(self):
        return self.title if self.title else "Post without title"

class Video(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, blank=True, null=True)
    video_file = models.FileField(upload_to='videos/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    @property
    def thumbnail1(self):
        if self.video_file:
            return get_thumbnail(self.video_file, "300x300", quality=99).url
        return None
    
    def __str__(self):
        return self.video_file.name

class Image(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, blank=True, null=True)
    image_file = models.ImageField(upload_to='images/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    @property
    def thumbnail2(self):
        if self.image_file:
            return get_thumbnail(self.image_file, "300x300", quality=99).url
        return None

    def __str__(self):
        return self.image_file.name

class SharedPost(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='shared_posts')
    shared_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='shared_by_user')
    shared_with = models.ManyToManyField(CustomUser, related_name='shared_with_user')
    shared_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.shared_by.username}"

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    content = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.content[:20] if self.content else "No content"

class PostLike(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)

    class Meta:
        unique_together = (("post", "user"), )

class UserFollow(models.Model):
    follower = models.ForeignKey(CustomUser, related_name='following_set', on_delete=models.CASCADE)
    following = models.ForeignKey(CustomUser, related_name='follower_set', on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.follower.username} follows {self.following.username}"
    
class FollowRequest(models.Model):
    from_user = models.ForeignKey(CustomUser, related_name='sent_requests', on_delete=models.CASCADE)
    to_user = models.ForeignKey(CustomUser, related_name='received_requests', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    accepted = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.from_user} follows {self.to_user}"
