from django.urls import path
from . import views

urlpatterns = [
   # path('', views.home, name='home'),
   path('signup/', views.signup_view, name='signup'),
   path('verify_otp/<str:user_id>/', views.verify_user_otp, name='verify_otp'),
   path('resend_otp/<str:user_id>/', views.resend_otp, name='resend_otp'),
   path('login/', views.login_view, name='login'),
   path('logout/', views.user_logout, name='logout'),
   path("reset_password/",views.reset_password_view,name="reset_password"),
   path("change_password/",views.change_password_view,name="change_password"),
   path("profile/<str:user_id>/",views.profile, name="profile"),
   path("update_profile/",views.update_profile, name="update_profile"),
   path('edit-profile/', views.edit_profile, name='edit_profile'),
   
   
   path("send_mobile_otp/<str:user_id>/",views.send_mobile_otp,name="send_mobile_otp"),
   path("verify_mobile_otp/<str:user_id>/",views.verify_mobile_otp,name="verify_mobile_otp"),
   path("resend_mobile_otp/",views.resend_mobile_otp,name="resend_mobile_otp"),
]