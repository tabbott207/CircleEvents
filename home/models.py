from django.db import models
from datetime import date
import uuid
from django.db import models
from django.contrib.auth.models import User

# Create your models here

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
    user = models.OneToOneField(User, on_delete=models.CASCADE)  # Links to the User model
    major = models.CharField(max_length=100, default="CCI", editable=False)  # Default value, non-editable
    concentration = models.CharField(max_length=100, blank=True, null=True)
    followers = models.ManyToManyField(
        'self',  # Refers to the same Profile model
        symmetrical=False,  # Following is not necessarily reciprocal
        related_name='following',  # Reverse relation for "following"
        blank=True  # Optional field
    )

    def __str__(self):
        return self.user.username