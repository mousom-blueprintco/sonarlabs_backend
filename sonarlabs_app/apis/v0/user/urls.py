from django.urls import path

from .views import RegisterUser,LoginUser,LogoutUser,TestProtectedView,RefreshAccessToken,VerifyUserRegisteration,ResetPasswordOTP,ResetPassword

urlpatterns = [
    path("register-user/", RegisterUser.as_view(), name="Register User"),
    path("login-user/", LoginUser.as_view(), name="Login User"),
    path("logout-user/", LogoutUser.as_view(), name="Logout User"),
    path("test-user/", TestProtectedView.as_view(), name="Test User Auth"),
    path("refresh-token/", RefreshAccessToken.as_view(), name="Refresh User Token"),
    path("verify-user-registeration/", VerifyUserRegisteration.as_view(), name="Verify User Token"),
    path("otp-reset-password/", ResetPasswordOTP.as_view(), name="OTP Password Reset"),
    path("reset-password/", ResetPassword.as_view(), name="Password Reset"),
]

