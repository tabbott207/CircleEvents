from django.db import models
from datetime import date
from django.conf import settings

import uuid
from django.db import models
from django.contrib.auth.models import User

# Create your models here
class RSVP(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    event = models.ForeignKey('Event', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    email = models.EmailField()
    comments = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"RSVP by {self.name} for {self.event.title}"

class Event(models.Model):
    title = models.CharField(max_length=200)  # Title of the event
    description = models.TextField(blank=True, null=True)  # Description of the event
    start_time = models.DateTimeField()  # Date and time when the event starts
    end_time = models.DateTimeField(blank=True, null=True)  # Optional end time for the event
    location = models.CharField(max_length=255, blank=True, null=True)  # Location of the event
    organizer = models.CharField(max_length=200, blank=True, null=True)  # Event organizer's name
    photo_url = models.URLField(blank=True, null=True)  # Optional photo URL
    localist_url = models.URLField(blank=True, null=True)  # URL for external event page
    google_url = models.URLField(blank=True, null=True)  # Optional Google Maps link or other details links

    def __str__(self):
        return self.title  # Display title in the admin and other contexts

class Contact(models.Model):
    name= models.CharField(max_length=122)
    email= models.CharField(max_length=122)
    phone= models.CharField(max_length=122)
    desc= models.TextField()

    def __str__(self):
        return self.name

class EventPage(models.Model):
    id = models.UUIDField( primary_key = True, default = uuid.uuid4, editable = False)
    title= models.CharField(max_length=122)
    header= models.CharField(max_length=122)
    desc= models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    location= models.TextField(default='')
    tag= models.CharField(max_length=122, default='')
    eventdate = models.IntegerField(default=1)
    eventday = models.TextField(default="")
    eventmonth = models.TextField(default="")
    eventyear = models.IntegerField(default=2020)
    organizer= models.CharField(max_length=122, default='')

    def __str__(self):
        return self.title


class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    major = models.CharField(max_length=100, default="CCI", editable=False)
    concentration = models.CharField(max_length=100, blank=True, null=True)

    picture = models.URLField(
        blank=True,
        null=True,
        default=f"{settings.STATIC_URL}img/logo-new.png",
        help_text="URL to the user's profile picture"
    )

    # Define relationships using 'related_name' to distinguish the fields
    following = models.ManyToManyField(
        'self',
        symmetrical=False,
        related_name='followers',
        blank=True
    )

    def __str__(self):
        return self.user.username

    def get_followers(self):
        """Return profiles of users who follow this user."""
        return self.followers.all()

    def get_following(self):
        """Return profiles this user is following."""
        return self.following.all()

    def suggest_followers_based_on_concentration(self):
        """Suggest profiles to follow based on similar concentration."""
        if not self.concentration:
            return Profile.objects.none()

        # Exclude the current user and already-followed profiles
        return Profile.objects.filter(
            concentration=self.concentration
        ).exclude(id=self.id).exclude(id__in=self.following.values_list('id', flat=True))