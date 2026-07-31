from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Notification

@login_required
def notifications_list_view(request):
    """View to display all in-app notifications for the logged-in user."""
    notifications = request.user.notifications.all()
    
    # Optionally mark unread notifications as read when viewing full page
    if request.GET.get('mark_all_read') == 'true':
        request.user.notifications.filter(is_read=False).update(is_read=True)
        messages.success(request, "All notifications marked as read.")
        return redirect('notifications_list')

    return render(request, 'notifications/notifications_list.html', {
        'notifications': notifications
    })

@login_required
def mark_notification_read_view(request, notification_id):
    """Mark a specific notification as read and redirect to target URL or notifications page."""
    notification = get_object_or_404(Notification, id=notification_id, recipient=request.user)
    notification.is_read = True
    notification.save()
    
    if notification.target_url:
        return redirect(notification.target_url)
    return redirect('notifications_list')
