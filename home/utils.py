def get_recommendations(user):
    from home.models import EventPage, Profile

    try:
        profile = Profile.objects.get(user=user)
        concentration = profile.concentration

        if concentration:
            recommendations = EventPage.objects.filter(matched_categories__icontains=concentration.name)
            # print("Debug: User concentration:", concentration.name)  # Debugging
            # print("Debug: Recommendations fetched:", recommendations)  # Debugging
            return recommendations
    except Profile.DoesNotExist:
        print("Debug: No profile found for user:", user)
        return EventPage.objects.none()

    return EventPage.objects.none()
