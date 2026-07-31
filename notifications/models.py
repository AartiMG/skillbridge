from django.db import models
from django.contrib.auth.models import User

class Notification(models.Model):
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    actor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_notifications', null=True, blank=True)
    verb = models.CharField(max_length=255)
    target_url = models.CharField(max_length=255, blank=True, default='')
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'

    def __str__(self):
        actor_name = self.actor.username if self.actor else "System"
        return f"Notification for {self.recipient.username}: {actor_name} {self.verb}"

def create_notification(recipient, actor, verb, target_url=''):
    """Helper to safely create an in-app notification."""
    if recipient != actor:  # Don't notify self
        return Notification.objects.create(
            recipient=recipient,
            actor=actor,
            verb=verb,
            target_url=target_url
        )
    return None
