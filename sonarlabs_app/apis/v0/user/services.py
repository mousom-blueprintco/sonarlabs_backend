from sonarlabs_app.models import User
import json

def get_user_by_email(email):
    try:
        user = User.objects.get(email=email)
        return user
    except:
        return None
    
def update_verify_token(email,verify_token):
    user = User.objects.get(email=email)
    user.verify_token = verify_token
    user.save()
 
def update_user_as_verified(user_id):
    user = User.objects.get(id=user_id)
    user.is_verified = True
    user.verify_token = None
    user.save()

def get_user_by_id(user_id):
    user = User.objects.get(id=user_id)
    return user

def add_otp_details(email,hashed_otp,otp_exp):
    user = User.objects.get(email=email)
    otp_details = {
                   "otp": hashed_otp,
                   "exp": otp_exp
                  }
    user.otp_details = json.dumps(otp_details)
    user.save()

def reset_user_password(email,reset_password):
    user = User.objects.get(email=email)
    user.set_password(reset_password)
    otp_details = {
                    "otp": None,
                    "exp": None
                  }
    user.otp_details = json.dumps(otp_details)
    user.save()