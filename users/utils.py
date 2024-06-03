import pyotp
from users.models import *
from django.core.mail import send_mail

def generate_otp():
    otp_secret = pyotp.random_base32()
    totp = pyotp.TOTP(otp_secret)
    return totp.now()

def send_otp_email(user_email, otp):
    subject = 'Password Reset OTP'
    message = f'Your OTP for password reset is: {otp}'
    from_email = 'shantharajuvedashree@gmail.com'
    recipient_list = [user_email]
    send_mail(subject, message, from_email, recipient_list)


def verify_otp(user_id, otp):
    try:
        password_reset_otp = PasswordResetOTP.objects.filter(user_id=user_id)[0]
        if password_reset_otp.otp == otp:
            return True
    except PasswordResetOTP.DoesNotExist:
        pass
    return False

def reset_password(user_id, new_password):
    user = CustomUser.objects.get(pk=user_id)
    user.set_password(new_password)
    user.save()
