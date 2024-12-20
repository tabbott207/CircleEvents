from django.db import models
from datetime import date
from django.conf import settings

import uuid
from django.db import models
from django.contrib.auth.models import User

# Create your models here
CONCENTRATION_CHOICES = [
    "Software Engineering",
    "Data Science",
    "Software Systems",
    "Cybersecurity",
    "Web and Mobile Applications",
    "AI Robotics and Gaming",
]

class Contact(models.Model):
    name= models.CharField(max_length=122)
    email= models.CharField(max_length=122)
    phone= models.CharField(max_length=122)
    desc= models.TextField()

    def __str__(self):
        return self.name

class EventPage(models.Model):
    id = models.UUIDField( primary_key = True, default = uuid.uuid4, editable = False)
    title= models.CharField(max_length=225)
    header= models.CharField(max_length=122)
    description= models.TextField()
    matched_categories = models.JSONField(default=list, blank=True)  #stores matched categories on a list
    created_at = models.DateTimeField(auto_now_add=True)
    location= models.TextField(default='')
    similarity_scores = models.FloatField(default=0.0)
    tag= models.CharField(max_length=122, default='')
    eventdate = models.IntegerField(default=1)
    eventday = models.TextField(default="")
    eventmonth = models.TextField(default="")
    eventyear = models.IntegerField(default=2020)
    organizer= models.CharField(max_length=122, default='')

    def __str__(self):
        return self.title

class Concentration(models.Model):
    name = models.CharField(max_length=255, unique=True)
    code = models.CharField(max_length=10, unique=True, null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = str(uuid.uuid4())[:8]  # Generate a unique 8-character code
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
    
class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    major = models.CharField(max_length=225, default="CCI", editable=False)
    concentration = models.ForeignKey(
        Concentration,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

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