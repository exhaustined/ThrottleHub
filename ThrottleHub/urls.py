from django.urls import path
from . views import *

urlpatterns = [
    path('',index,name='index'),
    path('login/',signin,name='login'),
    path('register/',register,name='register'),
    path('forget/',forget,name='forget'),
    path('newpassword/',verify_otp,name='newpass'),
    path('logout/',sign_out,name='logout'),
    path('uploadspot/',upload_spot,name='uploadspot'),
    path('profile/',profile,name='profile'),
    path('message/<int:id>/',messages,name='message'),
    path('addtogarage/',add_to_garage,name='add_to_garage'),
    path('follow_request/<int:following_id>/',follow_request,name='follow_request'),
    path('unfollow_request/<int:following_id>/',unfollow_request,name='unfollow_request'),
    path('search/',search,name='search'),
    path('like/',like_unlike,name='like'),
    path('post/<int:id>/',post_view,name='post_view')
]