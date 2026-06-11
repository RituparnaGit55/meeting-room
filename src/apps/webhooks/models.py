from django.db import models
from apps.accounts.models import User


class Webhook(models.Model):
    EVENT_CHOICES = [
        ("MEETING_CREATED", "Meeting Created"),
        ("MEETING_STARTED", "Meeting Started"),
        ("MEETING_ENDED", "Meeting Ended"),
        ("RECORDING_READY", "Recording Ready"),
        ("SUMMARY_READY", "Summary Ready"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="webhooks")
    url = models.URLField()
    event = models.CharField(max_length=50, choices=EVENT_CHOICES)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.event} - {self.url}"
