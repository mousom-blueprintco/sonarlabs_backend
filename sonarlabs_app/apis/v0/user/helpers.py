from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.tokens import AccessToken
import random
import hashlib
from django.utils import timezone 
from datetime import datetime
from django.core.mail import send_mail
import os
def gen_jwt_token(user):
    refresh = RefreshToken.for_user(user)
    data = {"access_token": str(refresh.access_token), "refresh_token": str(refresh)}
    return data

def blacklist_refresh_token(refresh_token):
    token = RefreshToken(refresh_token)
    token.blacklist()

def refresh_access_token(refresh_token):
 
    refresh = RefreshToken(refresh_token)
    refresh.verify()
    access_token = str(refresh.access_token)
    return access_token

def check_token_validity(verify_token):
    try:
        access_token = AccessToken(verify_token)
        user_id = access_token.payload['user_id']
        return user_id
    except Exception as err:
        print("qqq", err)
        return None
        
def generate_otp():
    return str(random.randint(100000, 999999))

def hash_otp(otp):
    return hashlib.sha256(otp.encode()).hexdigest()

def add_otp_expiration():
    current_time = timezone.now() 
    exp = current_time + timezone.timedelta(minutes=2) 
    otp_exp = exp.isoformat()
    return otp_exp

def check_otp_validity(user_otp_details, hashed_otp):
    current_time = timezone.now() 
    exp = user_otp_details["exp"] 
    otp_exp = datetime.fromisoformat(exp)
    if user_otp_details["otp"] == hashed_otp and current_time < otp_exp:
        return True
    
    return False

def send_email(subject,message,email):
          
    send_mail(
        subject=subject,
        message=message,
        from_email=os.environ.get("DEFAULT_FROM_EMAIL"),
        recipient_list=[email],
        fail_silently=False,
    )

def send_verification_email(email,verify_token, domain):
    subject = "Sonarlabs Verification"
    message = f'click the link to verify: {domain}verify/{verify_token}'
    send_email(subject,message,email)

def send_otp_email(email,otp):
    subject = "Sonarlabs Reset Password OTP"
    message = f'Your otp for password reset is {otp}'
    send_email(subject,message,email)





       
        