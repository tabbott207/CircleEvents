from django.contrib import admin
from django.urls import path
from home import views

urlpatterns = [
    path("", views.index, name="home"),
    path("signin", views.signin, name="signin"),
    path("signup", views.signup, name="signup"),
    path("contact", views.contact, name="contact"),
    path("logout", views.logout, name="logout"),
    path("event_detail/<str:id>", views.eventpage, name="eventpage"),
    path("event/<str:id>/", views.event_detail, name="event_detail"),
]