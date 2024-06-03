from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import CustomUser
from rest_framework.authtoken.serializers import AuthTokenSerializer
from django.contrib.auth import login
from knox.views import LoginView as KnoxLoginView
from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework import permissions, serializers, status
from rest_framework.generics import CreateAPIView,ListAPIView
from users.serializers import UserPasswordChangeSerializer
import django.contrib.auth.password_validation as validators
from django.core import exceptions
from users.filters import CustomUserFilter
from users.serializers import *
from django.db.models import Q
from users.utils import *

class CommonLogin(KnoxLoginView):
    """
    Common Login
    """
    permission_classes = (permissions.AllowAny,)

    def post(self, request, *args, **kwargs):
        identifier = request.data.get("identifier")
        password = request.data.get("password")
        
        user = None
        if identifier:
            user = CustomUser.objects.filter(
                Q(contact_number__icontains=identifier) | 
                Q(username__iexact=identifier) | 
                Q(email__iexact=identifier)
            ).first()
        
        if user:
            auth_data = {"username": user.username, "password": password}
            serializer = AuthTokenSerializer(data=auth_data)
            serializer.is_valid(raise_exception=True)
            user = serializer.validated_data["user"]
            
            login(request, user)
            response = super(CommonLogin, self).post(request, format=None)
            response.data.update({
                "id": user.id,
                "name": f"{user.first_name} {user.last_name}",
            })
            return response
        else:
            return Response(
                {"message": "User not found."},
                status=status.HTTP_400_BAD_REQUEST
            )


class UserRegistrationAPIView(APIView):

    def validate(self, data):
        if not data.get("email"):
            raise serializers.ValidationError({'message': 'Email is needed...!!!'})
        if CustomUser.objects.filter(email__iexact=data.get("email")).exists():
            raise serializers.ValidationError({'message': 'Email already exists. Please try to login...!!!'})
        
        if not data.get("username"):
            raise serializers.ValidationError({'message': 'Username is needed...!!!'})
        if CustomUser.objects.filter(username__iexact=data.get("username")).exists():
            raise serializers.ValidationError({'message': 'Username already exists. Please choose a different username...!!!'})
        
        if not data.get("contact_number"):
            raise serializers.ValidationError({'message': 'Contact number is needed...!!!'})
        if CustomUser.objects.filter(contact_number=data.get("contact_number")).exists():
            raise serializers.ValidationError({'message': 'Contact number already exists. Please try to login...!!!'})
        
        if data.get("password") != data.get("confirm_password"):
            raise serializers.ValidationError({'message': 'Passwords do not match...!!!'})
        
        return True

    def post(self, request):
        if self.validate(request.data):
            user = CustomUser(
                username=request.data.get("username"),
                email=request.data.get("email"),
                first_name=request.data.get("first_name"),
                last_name=request.data.get("last_name"),
                bio=request.data.get('bio', ''),
                location=request.data.get('location', ''),
                birth_date=request.data.get('birth_date', None),
                contact_number=request.data.get('contact_number', None),
                profile_picture=request.data.get('profile_picture', None),
                is_private=request.data.get('is_private', False)
            )
            user.set_password(request.data.get("password"))
            user.save()
            return Response(
                {
                    "message": "Signup successful",
                }, status=status.HTTP_201_CREATED
            )
        return Response(
            {
                "message": "Unsuccessful signup"
            }, status=status.HTTP_400_BAD_REQUEST
        )
    
class UserPasswordChangeApiView(CreateAPIView):
    queryset = CustomUser.objects.all().order_by("-id")
    serializer_class = UserPasswordChangeSerializer
    # permission_classes = (DjangoModelPermissions, )

    def validate(self, request):
        new_password = request.data.get("new_password")
        errors = dict()
        try:
            validators.validate_password(password=new_password)
        except exceptions.ValidationError as e:
            errors["message"] = list(e.messages)

        if errors:
            raise serializers.ValidationError(errors)
        return True

    def post(self, request, *args, **kwargs):
        if self.validate(request):
            old_password = request.data.get("old_password", None)
            new_password = request.data.get("new_password", None)
            confirmed_password = request.data.get("confirmed_password", None)
            if old_password and new_password and confirmed_password:
                if not self.request.user.check_password(old_password):
                    return Response(
                        {"success": False, "message": "Old Password is not matching."}
                    )

                if confirmed_password != new_password:
                    return Response(
                        {
                            "success": False,
                            "message": "New Password and Confirm Password not Matching.",
                        }
                    )

                self.request.user.set_password(new_password)
                self.request.user.save()
                return Response(
                    {
                        "success": True,
                        "message": "Password has been changed successfully.",
                    }
                )
            else:
                return Response(
                    {"success": False, "message": "Please Enter all Password Fields."}
                )
            
class UserList(ListAPIView):
    filterset_class = CustomUserFilter
    queryset=CustomUser.objects.all().order_by('-id')
    serializer_class=CustomUserSerializer

class FollowerFollowingListAPIView(APIView):
    def get(self, request, pk, format=None):
        try:
            user = CustomUser.objects.get(pk=pk)
        except CustomUser.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        followers = user.followers.all()
        serializer = UserDetailSerializer(followers, many=True)
        return Response(serializer.data)
class ForgetPasswordApiView(CreateAPIView):
    queryset = CustomUser.objects.all().order_by('-id') 
    serializer_class = Forgetpasswordserializer  
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        email = CustomUser.objects.get(username=request.data.get('email', None))
        new_password = request.data.get('new_password', None)
        confirmed_password = request.data.get('confirmed_password', None)
        if  new_password and confirmed_password:
            if confirmed_password != new_password:
                return Response({"success": False,"message":"New Password and Confirm Password not Matching."})  
        
            email.set_password(new_password)
            email.save()
            return Response({"success": True,"message":"Password has been changed successfully."})
        else:
            return Response({"success": False,"message":"Please Enter all Password Fields."})
        
class ForgotPassword(APIView):
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            return Response({"message": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        
        otp = generate_otp()
        PasswordResetOTP.objects.create(user=user, otp=otp)

        send_otp_email(email, otp)

        return Response({"message": "OTP sent successfully"}, status=status.HTTP_200_OK)

class ResetPassword(APIView):
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        otp = request.data.get('otp')
        new_password = request.data.get('new_password')
        user = CustomUser.objects.filter(email=email)

        if not verify_otp(user[0].id, otp):
            return Response({"message": "Invalid OTP"}, status=status.HTTP_400_BAD_REQUEST)
        
        reset_password(user[0].id, new_password)

        return Response({"message": "Password reset successfully"}, status=status.HTTP_200_OK)
        
