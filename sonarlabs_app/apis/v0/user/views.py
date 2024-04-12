from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import RegisterUserSerializer, LoginUserSerializer
from django.contrib.auth import authenticate
from django.contrib.auth.models import update_last_login
from .helpers import gen_jwt_token,blacklist_refresh_token,refresh_access_token,check_token_validity,generate_otp,hash_otp,add_otp_expiration,check_otp_validity,send_verification_email,send_otp_email
from sonarlabs_app.base.response_codes import SUCCESS_CODES, ERROR_CODES
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import status
from sonarlabs_app.models import User
from .services import get_user_by_email,update_verify_token,update_user_as_verified,get_user_by_id,add_otp_details,reset_user_password
import json

class RegisterUser(APIView):
    '''
    Register the user to sonar app
    '''
    def post(self,request):

        email = request.data['email']
        user = get_user_by_email(email)
        domain = request.META['HTTP_REFERER']
        # check verify token validity if user registered but is not verified
        if user:
            # if user.is_verified:
                return Response({"message": ERROR_CODES['E_REGISTER']}, status=status.HTTP_400_BAD_REQUEST)
            
            # user_id = check_token_validity(user.verify_token)

            # # send email with same verification token if verify token is valid
            # if user_id:
            #     # send_verification_email(email,verify_token,domain)
            #     return Response({"message": SUCCESS_CODES['S_REGISTER'],"verify_token": user.verify_token}, status=status.HTTP_200_OK)

            # # generate new verification token if verify token is expired
            # data = gen_jwt_token(user)
            # verify_token = data['access_token']

            # update_verify_token(email,verify_token)

            # # send email with new verification token
            # # send_verification_email(email,verify_token,domain)

            # return Response({"message": SUCCESS_CODES['S_REGISTER'],"verify_token": verify_token}, status=status.HTTP_200_OK)  
        
        # register user and send verification token  
        else :
            serializer = RegisterUserSerializer(data=request.data)

            # register the user and send verification email
            if serializer.is_valid():
                user = serializer.save()

                # data = gen_jwt_token(user)
                # verify_token = data['access_token']

                # update_verify_token(email,verify_token)

                # # send email with verification token
                # # send_verification_email(email,verify_token,domain)

                return Response({"message": SUCCESS_CODES['S_REGISTER']}, status=status.HTTP_200_OK)
                
        return Response({"message": ERROR_CODES['E_REGISTER']}, status=status.HTTP_400_BAD_REQUEST)      
                       
class LoginUser(APIView):
    '''
    User login to sonar app
    '''
    def post(self,request):

        serializer = LoginUserSerializer(data=request.data)

        if serializer.is_valid():
            email = serializer.validated_data.get("email")
            password = serializer.validated_data.get("password")

            # check the user login credenetials and send tokens
            user = authenticate(request, email=email, password=password)

            if user:
                data = gen_jwt_token(user)
                update_last_login(None, user)

                return Response({"message": SUCCESS_CODES['S_LOGIN'], "data": data }, status=status.HTTP_200_OK)
            
        return Response({"message": ERROR_CODES['E_LOGIN']}, status=status.HTTP_400_BAD_REQUEST)       
            
class LogoutUser(APIView):
    '''
    Logout user from sonar app
    '''
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]  

    def post(self,request):
        
        # blacklist the user's refresh token
        try:
            refresh_token = request.data["refresh_token"]
            blacklist_refresh_token(refresh_token)

            return Response({"message": SUCCESS_CODES["S_LOGOUT"]}, status = status.HTTP_200_OK)
        
        except:
            return Response({"message": ERROR_CODES['E_LOGOUT']}, status=status.HTTP_400_BAD_REQUEST)
                
    
class RefreshAccessToken(APIView):
    '''
    Refresh user jwt access token 
    '''
    def post(self,request):

        # regenerate new access token based on the user's refresh token
        try:
            refresh_token = request.data["refresh_token"]
            new_access_token = refresh_access_token(refresh_token)

            return Response({"message": SUCCESS_CODES["S_REFRESH_TOKEN"], "new_access_token": new_access_token}, status = status.HTTP_200_OK)
        
        except:
            return Response({"message": ERROR_CODES['E_REFRESH_TOKEN']}, status=status.HTTP_400_BAD_REQUEST)

    
class VerifyUserRegisteration(APIView):
    '''
    Verify the user registeration
    '''
    def post(self,request):
        
        try:
            verify_token = request.data['verify_token']
            user_id = check_token_validity(verify_token)

            # verify the user's registeration and update user as verified user
            if user_id:
                user = get_user_by_id(user_id)
                update_user_as_verified(user_id)

                data = gen_jwt_token(user)
                update_last_login(None, user)

                return Response({"message": SUCCESS_CODES['S_LOGIN'], "data": data }, status=status.HTTP_200_OK)
            
            else:
                return Response({"message": ERROR_CODES['E_VERIFY_TOKEN_INVALID']}, status=status.HTTP_400_BAD_REQUEST)
            
        except:
            return Response({"message": ERROR_CODES['E_VERIFY_TOKEN_INVALID']}, status=status.HTTP_400_BAD_REQUEST)

    
class ResetPasswordOTP(APIView):
    '''
    Send otp to reset passowrd
    '''
    def post(self,request):
        try:
            email = request.data['email']
            user = get_user_by_email(email)

            # send otp for user's reset password request
            if user:
               otp = generate_otp()  
               hashed_otp = hash_otp(otp)
               otp_exp = add_otp_expiration()
               
               add_otp_details(email,hashed_otp,otp_exp)

               # send email with otp
            #    send_otp_email(email,otp)

               return Response({"message": SUCCESS_CODES['S_OTP_SENT'], "otp": otp }, status=status.HTTP_200_OK)

            return Response({"message": ERROR_CODES['E_NO_OTP_SENT']}, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as err:
            return Response({"message": ERROR_CODES['E_NO_OTP_SENT']}, status=status.HTTP_400_BAD_REQUEST)
        
class ResetPassword(APIView):
    '''
    Reset the user passoword 
    '''
    def put(self, request):

        try:
            email = request.data['email']
            otp = request.data['otp']
            reset_password = request.data['reset_password']

            user = get_user_by_email(email)
            hashed_otp = hash_otp(otp)

            # reset user password and update in db if otp is valid
            if user:
                user_otp_details = json.loads(user.otp_details)
                is_otp_valid = check_otp_validity(user_otp_details,hashed_otp)

                if not is_otp_valid:
                    return Response({"message": ERROR_CODES['E_OTP_INVALID']}, status=status.HTTP_400_BAD_REQUEST)
                
                reset_user_password(email,reset_password)

                return Response({"message": SUCCESS_CODES['S_RESET_PASSWORD']}, status=status.HTTP_200_OK)
            
            return Response({"message": ERROR_CODES['E_RESET_PASSWORD_FAILED']}, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as err:
            return Response({"message": ERROR_CODES['E_RESET_PASSWORD_FAILED']}, status=status.HTTP_400_BAD_REQUEST)
        
                  
              
class TestProtectedView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]  

    def get(self, request):
        return Response({"message": "Hello Test User"}, status=status.HTTP_200_OK)