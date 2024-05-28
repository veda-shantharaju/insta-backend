from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractUser
from phonenumber_field.modelfields import PhoneNumberField
from sorl.thumbnail import get_thumbnail

class CustomUser(AbstractUser):
    bio = models.TextField(max_length=500, blank=True)
    location = models.CharField(max_length=30, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    contact_number = PhoneNumberField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    followers = models.ManyToManyField('self', symmetrical=False, related_name='following', blank=True)
    is_private = models.BooleanField(default=False, null=True, blank=True)

    @property
    def thumbnail3(self):
        if self.profile_picture:
            return get_thumbnail(self.profile_picture, "300x300", quality=99).url
        return None

    def __str__(self):
        return self.username

    def is_following(self, user):
        return self.following.filter(pk=user.pk).exists()

    def unfollow(self, user):
        if self.is_following(user):
            self.following.remove(user)
            return True
        return False