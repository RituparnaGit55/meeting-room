from django.db import models
from apps.accounts.models import User


class Notification(models.Model):
    TYPE_CHOICES = [
        ("MEETING_INVITE", "Meeting Invite"),
        ("MEETING_START", "Meeting Start"),
        ("TASK_ASSIGNED", "Task Assigned"),
        ("MESSAGE", "New Message"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications")
    type = models.CharField(max_length=50, choices=TYPE_CHOICES)
    title = models.CharField(max_length=255)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.user.email}"
