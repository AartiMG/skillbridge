def unread_notifications_count(request):
    """Context processor providing unread notifications count across all templates."""
    if request.user.is_authenticated:
        return {
            'unread_notifications_count': request.user.notifications.filter(is_read=False).count()
        }
    return {'unread_notifications_count': 0}
