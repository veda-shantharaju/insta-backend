from rest_framework import serializers
from .models import CustomUser

class CustomUserSerializer(serializers.ModelSerializer):
    thumbnail3=serializers.SerializerMethodField()
    def get_thumbnail3(self, obj):
        if obj.profile_picture:
            return self.context.get("request").build_absolute_uri(obj.thumbnail3)
    class Meta:
        model = CustomUser
        fields = ['id', 
                  'username', 
                  'first_name', 
                  'last_name',
                  'email', 
                  'bio', 
                  'location', 
                  'birth_date',
                  'contact_number',
                  'profile_picture',
                  'thumbnail3',
                  'followers',
                  'is_private',
                  'is_staff', 
                  'is_superuser', 
                  'is_active',
                  'last_login', 
                  'date_joined'
                  ]
        
class CustomUserMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 
                  'username',
                  ]
        
class UserPasswordChangeSerializer(serializers.ModelSerializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    confirmed_password = serializers.CharField(required=True)

    class Meta:
        model = CustomUser
        fields = ("id", "old_password", "new_password", "confirmed_password")

    def validate(self, data):

        if not self.context["request"].user.check_password(data.get("old_password")):
            raise serializers.ValidationError({"message": "Wrong password."})

        if data.get("confirmed_password") != data.get("new_password"):
            raise serializers.ValidationError(
                {"message": "Password must be confirmed correctly."}
            )

        return data

    def update(self, instance, validated_data):
        instance.set_password(validated_data["password"])
        instance.save()
        return instance
    
class FollowSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'profile_picture']


class UserDetailSerializer(serializers.ModelSerializer):
    follower_count = serializers.SerializerMethodField()
    following_count = serializers.SerializerMethodField()
    followers = FollowSerializer(many=True)
    following = FollowSerializer(many=True)

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'bio', 'location', 'birth_date', 'contact_number', 'profile_picture', 'follower_count', 'following_count', 'followers', 'following']

    def get_follower_count(self, obj):
        return obj.followers.count()

    def get_following_count(self, obj):
        return obj.following.count()