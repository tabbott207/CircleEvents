from django.contrib import admin
from django.urls import path
from home import views

urlpatterns = [
    path("", views.index, name="home"),
    path('register/', views.signup, name='signup'),
    path('login/', views.signin, name='signin'),
    path('logout/', views.logout, name='logout'),
    path("contact", views.contact, name="contact"),
    path('event/<str:event_id>/', views.event_detail, name='event_detail'),
]