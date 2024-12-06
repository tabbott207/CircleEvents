from django.contrib import admin
from django.urls import path
from home import views

urlpatterns = [
    path("", views.index, name="home"),
    # path('register/', views.signup, name='signup'),
    # path('login/', views.signin, name='signin'),
    path('profile/', views.profile, name='profile'),  # Add this line for the profile page
    path('signup/', views.signup, name='signup'),
    path('signin/', views.signin, name='signin'),
    path('logout/', views.logout, name='logout'),
    path("contact", views.contact, name="contact"),
    path("profile", views.profile, name="contact"),
    path('event/<str:event_id>/', views.event_detail, name='event_detail'),
    path('follow/<int:user_id>/', views.follow_user, name='follow_user'),
    path('unfollow/<int:user_id>/', views.unfollow_user, name='unfollow_user'),

]