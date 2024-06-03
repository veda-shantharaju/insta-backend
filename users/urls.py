from django.urls import path
from users.views import *
from knox import views as knox_views

urlpatterns = [
    path('signup/',UserRegistrationAPIView.as_view(), name='user-signup'),
    path('login/',CommonLogin.as_view(), name='user-login'),
    path("logout/", knox_views.LogoutView.as_view(), name="knox_logout"),
    path("user-change-password/",UserPasswordChangeApiView.as_view(),name="password-change",),
    path('userlist/',UserList.as_view(), name='user-list'),
    path('follower-following/<int:pk>/', FollowerFollowingListAPIView.as_view(), name='follower-following-list'),

    path('forget-password/', ForgetPasswordApiView.as_view(), name="forget-password"),

    path('forgot-password/', ForgotPassword.as_view(), name="forgot-password"),
    path('reset-password/', ResetPassword.as_view(), name="reset-password"),


]