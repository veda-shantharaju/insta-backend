from rest_framework import generics
from .models import *
from .serializers import *
from rest_framework.generics import CreateAPIView,ListAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import ast
from django.http import Http404
from rest_framework.permissions import IsAuthenticated
from datetime import datetime
from posts.filters import PostFilter


class PostCreateAPIView(CreateAPIView):
    def post(self, request, *args, **kwargs):
        # Create the post object
        post = Post.objects.create(
            user_id=self.request.user.id,
            title=request.data.get("title"),
            description=request.data.get("description")
        )

        # Handle video uploads
        videos = request.FILES.getlist('videos')
        for video_file in videos:
            Video.objects.create(
                post_id=post.id,
                video_file=video_file
            )

        # Handle image uploads
        images = request.FILES.getlist('images')
        for image_file in images:
            Image.objects.create(
                post_id=post.id,
                image_file=image_file
            )

        return Response(
            {
                "message": "Posted successfully",
            },
            status=status.HTTP_201_CREATED
        )

class PostListAPIView(ListAPIView):
    serializer_class = PostListSerializer
    permission_classes = [IsAuthenticated]
    filterset_class = PostFilter
    def get_queryset(self):
        return (
            Post.objects.filter(
                user_id = self.request.user.id 
            ).order_by("-id").distinct())

class PostDelete(APIView):
    permission_classes = [IsAuthenticated]
    """
    delete a post instance.
    """
    def get_object(self, pk):
        try:
            return Post.objects.get(pk=pk,user_id = self.request.user.id )
        except Post.DoesNotExist:
            raise Http404
        
    def delete(self, request, pk, format=None):
        post = self.get_object(pk)
        post.delete()
        return Response({
                "message": "Post deleted",
            }, status=status.HTTP_204_NO_CONTENT)
    
class FollowRequestCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, *args, **kwargs):
        from_user = request.user
        to_user_id = request.data.get('to_user')

        try:
            to_user = CustomUser.objects.get(id=to_user_id)
        except CustomUser.DoesNotExist:
            return Response({"error": "User does not exist."}, status=status.HTTP_404_NOT_FOUND)

        if from_user == to_user:
            return Response({"error": "You cannot follow yourself."}, status=status.HTTP_400_BAD_REQUEST)

        if to_user.is_private:
            # Check if there's already a pending request
            existing_request = FollowRequest.objects.filter(from_user=from_user, to_user=to_user, accepted=False).first()
            if existing_request:
                return Response({"error": "There is already a pending follow request."}, status=status.HTTP_400_BAD_REQUEST)

            # Create a new follow request
            follow_request = FollowRequest(from_user=from_user, to_user=to_user)
            follow_request.save()

            return Response({"message": "Follow request sent successfully."}, status=status.HTTP_201_CREATED)
        else:
            # If the account is public, add the user to the followers list directly
            to_user.followers.add(from_user)
            return Response({"message": f"You are now following {to_user.username}."}, status=status.HTTP_200_OK)
    
class FollowRequestResponseAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, *args, **kwargs):
        to_user = request.user
        follow_request_id = request.data.get('follow_request_id')
        response = request.data.get('response')

        try:
            follow_request = FollowRequest.objects.get(id=follow_request_id, to_user=to_user, accepted=False)
        except FollowRequest.DoesNotExist:
            return Response({"error": "Follow request not found."}, status=status.HTTP_404_NOT_FOUND)

        if response == 'accept':
            follow_request.accepted = True
            follow_request.save()
            from_user = follow_request.from_user
            to_user.followers.add(from_user)
            return Response({"message": "Follow request accepted."}, status=status.HTTP_200_OK)
        elif response == 'reject':
            follow_request.delete()
            return Response({"message": "Follow request rejected."}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Invalid response."}, status=status.HTTP_400_BAD_REQUEST)
        
class PostUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated]
    queryset = Post.objects.all()
    # serializer_class = PostSerializer  # Define your serializer here

    def put(self, request, *args, **kwargs):
        post_id = request.data.get('post_id')

        try:
            # Ensure the post belongs to the current user
            instance = Post.objects.get(id=post_id, user_id=self.request.user.id)
        except Post.DoesNotExist:
            return Response(
                {"message": "Post not found or you do not have permission to edit this post."},
                status=status.HTTP_404_NOT_FOUND
            )

        # Update post fields
        instance.title = request.data.get("title", instance.title)
        instance.description = request.data.get("description", instance.description)
        instance.is_archived = request.data.get("is_archived", instance.is_archived)
        instance.updated_at=datetime.now()
        instance.save()

        # Handle video deletions
        delete_videos = request.data.get('delete_videos', [])
        for video_id in delete_videos:
            try:
                video = Video.objects.get(pk=video_id, post=instance)
                video.delete()
            except Video.DoesNotExist:
                pass

        # Handle image deletions
        delete_images = request.data.get('delete_images', [])
        for image_id in delete_images:
            try:
                image = Image.objects.get(pk=image_id, post=instance)
                image.delete()
            except Image.DoesNotExist:
                pass
        return Response(
            {
                "message": "Post updated successfully",
            },
            status=status.HTTP_200_OK
        )
    
class SharePostView(generics.CreateAPIView):
    # serializer_class = SharedPostListSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        q=SharedPost.objects.create(
            post_id = request.data.get('post_id'),
            shared_by_id=self.request.user.id
        )
        q.shared_with.add(*request.data.get("shared_with"))
        return Response(
                {"detail": "Post shared successfully."},
                status=status.HTTP_201_CREATED
            )

class CommentCreateView(generics.CreateAPIView):
    # serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        q=Comment.objects.create(
            post_id = request.data.get('post_id'),
            user_id=self.request.user.id,
            content = request.data.get('content')
        )
        return Response(
                {"detail": "commented successfully."},
                status=status.HTTP_201_CREATED
            )

class CommentDeleteView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        comment_id = request.data.get("comment_id")

        if not comment_id:
            return Response({"detail": "comment_id is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            comment = Comment.objects.get(id=comment_id, user_id=self.request.user.id)
            comment.delete()
            return Response({"detail": "Comment deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
        except Comment.DoesNotExist:
            return Response({"detail": "Comment not found or you do not have permission to delete it."},
                            status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class CommentEditView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, *args, **kwargs):
        comment_id = request.data.get("comment_id")
        content = request.data.get("content")

        if not comment_id or not content:
            return Response(
                {"detail": "comment_id and content are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            comment = Comment.objects.get(id=comment_id, user_id=self.request.user.id)
            comment.content = content
            comment.save()
            return Response(
                {"detail": "Comment edited successfully."},
                status=status.HTTP_200_OK
            )
        except Comment.DoesNotExist:
            return Response(
                {"detail": "Comment not found or you do not have permission to edit it."},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

class PostLikeView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        post_id = request.data.get('post_id')

        if not post_id:
            return Response(
                {"detail": "post_id is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            post = Post.objects.get(id=post_id)
            user = request.user

            # Check if the user has already liked the post
            post_like, created = PostLike.objects.get_or_create(post=post, user=user)

            if not created:
                post_like.delete()
                return Response({"message": "Post unliked"}, status=status.HTTP_204_NO_CONTENT)
            
            return Response({"message": "Post liked"}, status=status.HTTP_201_CREATED)

        except Post.DoesNotExist:
            return Response(
                {"detail": "Post not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        
class UnfollowAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        to_user_id = request.data.get('to_user')

        try:
            to_user = CustomUser.objects.get(id=to_user_id)
        except CustomUser.DoesNotExist:
            return Response({"error": "User does not exist."}, status=status.HTTP_404_NOT_FOUND)

        from_user = request.user

        # Ensure from_user is following to_user before unfollowing
        if not from_user.is_following(to_user):
            return Response({"error": "You are not following this user."}, status=status.HTTP_400_BAD_REQUEST)

        # Unfollow the user
        from_user.unfollow(to_user)

        return Response({"message": f"You have unfollowed {to_user.username}."}, status=status.HTTP_200_OK)