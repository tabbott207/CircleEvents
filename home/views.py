from django.shortcuts import render, redirect, get_object_or_404
from home.models import Contact, EventPage
from django.contrib import messages
from django.db.models import Q
from django.contrib.auth.models import User, auth
from django.contrib.auth import authenticate, login
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from googleapiclient.discovery import build
from google.oauth2 import service_account
from .models import Profile
from datetime import datetime
from .models import Concentration
from django.core.paginator import Paginator
import requests
from .utils import get_recommendations
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
import hashlib
import random
import os

# Constants
EMAIL_SENDER = settings.EMAIL_HOST_USER
GOOGLE_CALENDAR_ID = 'cci-events@uncc.edu'
SERVICE_ACCOUNT_FILE = os.path.join(settings.BASE_DIR, 'home/keys', 'circleapp-444305-20546ffa6de4.json')
GOOGLE_RECAPTCHA_SECRET_KEY = settings.GOOGLE_RECAPTCHA_SECRET_KEY
LOCALIST_API_URL = "https://campusevents.charlotte.edu/api/2/events?group_id=Health%20and%20Wellbeing"

# Helper function to fetch Google Calendar events
def get_calendar_events():
    SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
    try:
        credentials = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES
        )
        service = build('calendar', 'v3', credentials=credentials)
        now = datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time

        events_result = service.events().list(
            calendarId=GOOGLE_CALENDAR_ID, timeMin=now, maxResults=10, singleEvents=True,
            orderBy='startTime'
        ).execute()
        events = events_result.get('items', [])

        # Generate consistent IDs and return event details
        return [
            {
                'id': generate_event_id({
                    'title': event.get('summary', 'No Title'),
                    'start_time': event['start'].get('dateTime', event['start'].get('date')),
                }),
                'title': event.get('summary', 'No Title'),
                'start_time': event['start'].get('dateTime', event['start'].get('date')),
                'location': event.get('location', 'TBA'),
                'google_url': event.get('htmlLink', '#'),  # Add link for Google events
                'description': event.get('description', 'Description not available.')
            }
            for event in events
        ]
    except Exception as e:
        print(f"Error fetching calendar events: {e}")
        return []

    
# Helper function to fetch Mindfulness events from Localist API
def get_mindfulness_events():
    LOCALIST_API_URL = "https://campusevents.charlotte.edu/api/2/events?group_id=Health%20and%20Wellbeing"
    try:
        response = requests.get(LOCALIST_API_URL)
        if response.status_code == 200:
            data = response.json()
            events = []

            for event_data in data.get('events', []):
                # Extract event details
                event = {
                    'title': event_data['event'].get('title', 'No Title'),
                    'start_time': event_data['event']['event_instances'][0]['event_instance'].get('start', 'TBD'),
                    'location': event_data['event'].get('location_name', 'TBA'),
                    'photo_url': event_data['event'].get('photo_url', None),
                    'localist_url': event_data['event'].get('localist_url', '#'),
                    'description': event_data['event'].get('description_text', 'Description not available.'),
                }
                # Generate unique IDs using the generate_event_id function
                event['id'] = generate_event_id(event)
                events.append(event)
            return events
    except Exception as e:
        print(f"Error fetching Mindfulness events: {e}")
    return []

# View: Home page with events
# View: Home page with events
def index(request):
    # Fetch events from both sources
    career_events = get_calendar_events()
    mindfulness_events = get_mindfulness_events()

    # Apply generated IDs
    for event in career_events + mindfulness_events:
        event['id'] = generate_event_id(event)

    # Combine and sort events by start time
    all_events = career_events + mindfulness_events
    all_events.sort(key=lambda e: e['start_time'])  # Sort events chronologically

    # Implement pagination
    paginator = Paginator(all_events, 6)  # Show 6 events per page
    page_number = request.GET.get('page', 1)  # Get the current page from the request
    page_obj = paginator.get_page(page_number)  # Fetch events for the current page

    return render(request, 'index.html', {
        'page_obj': page_obj,  # Paginated events
        'mindfulness_events': mindfulness_events,  # Still passed for the mindfulness tab
        'career_events': career_events,  # Still passed for the career tab
    })

# View: User Sign-In
def signin(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username=username, password=password)
        if user:
            auth.login(request, user)
            try:
                # Check if the user's profile has a concentration
                profile = Profile.objects.get(user=user)
                if not profile.concentration:  # Redirect if concentration is not set
                    messages.warning(request, "Please update your concentration.")
                    return redirect('profile')  # Redirect to the profile page
            except Profile.DoesNotExist:
                # Handle case where profile is missing
                messages.error(request, "Profile not found. Contact support.")
                return redirect('signin')

            messages.success(request, "Successfully logged in!")
            return redirect('home')  # Redirect to home if concentration exists
        else:
            messages.error(request, "Invalid credentials.")
            return redirect('signin')
    return render(request, 'signin.html')

# View: User Sign-Up
def signup(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email')
        firstname = request.POST.get('firstname', '')

        # Check if username or email already exists
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username is already taken.")
            return redirect('signup')
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email is already registered.")
            return redirect('signup')

        try:
            # Create the user
            user = User.objects.create_user(username=username, password=password, email=email, first_name=firstname)
            user.save()


            # Authenticate and log the user in
            user = authenticate(username=username, password=password)
            if user:
                login(request, user)
                messages.success(request, "Account created successfully! Please update your profile.")
                return redirect('profile')  # Redirect to profile page

        except Exception as e:
            messages.error(request, f"Error creating account: {e}")
    return render(request, 'signup.html')

# View: Contact Form
def contact(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        desc = request.POST.get('textbox')
        recaptcha_response = request.POST.get('g-recaptcha-response')

        # Verify reCAPTCHA
        data = {'secret': GOOGLE_RECAPTCHA_SECRET_KEY, 'response': recaptcha_response}
        r = requests.post('https://www.google.com/recaptcha/api/siteverify', data=data)
        result = r.json()

        if result.get('success'):
            Contact.objects.create(name=name, email=email, phone=phone, desc=desc)
            messages.success(request, "Your response has been sent!")

            # Email the user with event details
            try:
                event = get_object_or_404(EventPage, id=desc)
                context = {
                    'name': name,
                    'phone': phone,
                    'event': event.title,
                    'location': event.location,
                    'desc': event.desc,
                    'organizer': event.organizer,
                }
                message = render_to_string('email/registration_complete_email.html', context)
                send_mail(
                    'Registration Completed | Circle',
                    strip_tags(message),
                    EMAIL_SENDER,
                    [email],
                    fail_silently=False,
                    html_message=message
                )
            except Exception as e:
                messages.error(request, f"Error sending email: {e}")
            return redirect('index')
        else:
            messages.error(request, "Invalid reCAPTCHA. Please try again.")
            return redirect('contact')
    return render(request, "contact.html")

# View: Event Page
def eventpage(request, id):
    event = get_object_or_404(EventPage, id=id)
    return render(request, 'eventpage.html', {'event': event})

def event_detail(request, event_id):
    # Fetch Google Calendar and Localist events
    google_events = get_calendar_events()
    localist_events = get_mindfulness_events()

    # Search for the event by ID in both sources
    google_event = next((e for e in google_events if e['id'] == event_id), None)
    localist_event = next((e for e in localist_events if e['id'] == event_id), None)

    # Find the event or return a 404 page
    event = google_event or localist_event
    if not event:
        return render(request, '404.html', status=404)

    # Ensure a `localist_url` or `google_url` exists in the event context
    if google_event:
        event['localist_url'] = event.get('google_url', '#')
    elif localist_event:
        event['google_url'] = event.get('localist_url', '#')

    # Render the event detail page
    return render(request, 'event_detail.html', {'event': event})

# View: Logout
def logout(request):
    auth.logout(request)
    messages.success(request, "Logged out successfully.")
    return redirect('/')
def generate_event_id(event):
    # Generate a unique hash using title and start time
    unique_str = f"{event.get('title', 'unknown')}-{event.get('start_time', 'unknown')}"
    return hashlib.md5(unique_str.encode()).hexdigest()
  
  
# View: User Profile
@login_required
def profile(request):
    user = request.user
    profile, created = Profile.objects.get_or_create(user=user)

    if request.method == 'POST':
        # Update User fields
        user.username = request.POST.get('username', user.username)
        user.email = request.POST.get('email', user.email)
        user.first_name = request.POST.get('first_name', user.first_name)  # Capture and update first_name
        user.save()

        # Update Profile fields
        profile.major = request.POST.get('major', profile.major)

        concentration_name = request.POST.get('concentration')
        if concentration_name:
            try:
                concentration = Concentration.objects.get(name=concentration_name)
                profile.concentration = concentration
            except Concentration.DoesNotExist:
                messages.error(request, "Invalid concentration selected.")
                return redirect('profile')

        profile.save()

        messages.success(request, "Profile updated successfully!")
        return redirect('home')  # Redirect to home after updating

    # Get followers, following, and suggestions for the template
    followers = profile.get_followers()
    following = profile.get_following()
    suggestions = profile.suggest_followers_based_on_concentration()
    concentrations = Concentration.objects.all()

    # Render template with context
    return render(request, 'profile.html', {
        'user': user,
        'profile': profile,
        'followers': followers,
        'following': following,
        'suggestions': suggestions,
        'concentrations': concentrations,
    })


@login_required
def follow_user(request, user_id):
    target_user = get_object_or_404(User, id=user_id)
    target_profile, created = Profile.objects.get_or_create(user=target_user)

    if target_profile not in request.user.profile.following.all():
        request.user.profile.following.add(target_profile)
        messages.success(request, f"You are now following {target_user.username}!")
    else:
        messages.info(request, f"You are already following {target_user.username}.")

    return redirect('profile')

@login_required
def unfollow_user(request, user_id):
    target_user = get_object_or_404(User, id=user_id)
    target_profile, created = Profile.objects.get_or_create(user=target_user)

    if target_profile in request.user.profile.following.all():
        request.user.profile.following.remove(target_profile)
        messages.success(request, f"You have unfollowed {target_user.username}.")
    else:
        messages.info(request, f"You were not following {target_user.username}.")

    return redirect('profile')

def index(request):
    # Fetch events from both sources
    career_events = get_calendar_events()
    mindfulness_events = get_mindfulness_events()

    # Combine and sort events by start time
    all_events = career_events + mindfulness_events
    all_events.sort(key=lambda e: e['start_time'])

    # Search functionality
    query = request.GET.get('q', '')  # Get the query parameter
    if query:
        all_events = [
            event for event in all_events
            if query.lower() in event.get('title', '').lower() or query.lower() in event.get('location', '').lower()
        ]

    # Implement pagination
    paginator = Paginator(all_events, 6)  # Show 6 events per page
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    # Select 3 random events for the "Recommended Events" section
    recommended_events = random.sample(all_events, min(len(all_events), 3))

    return render(request, 'index.html', {
        'page_obj': page_obj,  # Paginated events
        'mindfulness_events': mindfulness_events,  # Still passed for the mindfulness tab
        'career_events': career_events,  # Still passed for the career tab
        'recommended_events': recommended_events,  # Recommended events section
        'query': query,  # Pass the query back to the template
    })

def event_recommendations(request):
    if not request.user.is_authenticated:
        return render(request, 'not_authenticated.html')

    recommendations = get_recommendations(request.user)
    paginator = Paginator(recommendations, 6)  # Show 6 events per page
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    return render(request, 'recommendations.html', {
        'page_obj': page_obj,  # Paginated recommendations
    })


    return render(request, 'recommendations.html', {'page_obj': page_obj})

def mood_page(request):
    # Define moods and their corresponding emojis
    moods = {
        'Angry': '😡',
        'Excited': '🤩',
        'Depressed': '😢',
        'Anxious': '😟',
        'Good': '😎',
        'Happy': '😊',
        'Sad': '😭',
        'Shy': '🙈',
        'Tired': '😴',
    }

    # Get the selected mood from the query parameters
    selected_mood = request.GET.get('mood', None)
    selected_emoji = moods.get(selected_mood)  # Get the emoji for the selected mood
    quote = None

    if selected_mood:
        # Fetch a quote using ZenQuotes API
        response = requests.get("https://zenquotes.io/api/random")
        if response.status_code == 200:
            data = response.json()
            quote = data[0]['q'] if len(data) > 0 else "No quote available."

    # Context to pass to the template
    context = {
        'selected_mood': selected_mood,
        'selected_emoji': selected_emoji,
        'quote': quote,
        'moods': moods,  # Include the moods dictionary for displaying mood options
    }

    return render(request, 'mood.html', context)