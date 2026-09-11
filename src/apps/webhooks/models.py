from django.db import models
from apps.accounts.models import User


class Webhook(models.Model):
    EVENT_CHOICES = [
        ("MEETING_CREATED", "Meeting Created"),
        ("MEETING_STARTED", "Meeting Started"),
        ("MEETING_ENDED", "Meeting Ended"),
        ("PARTICIPANT_JOINED", "Participant Joined"),
        ("PARTICIPANT_LEFT", "Participant Left"),
        ("RECORDING_READY", "Recording Ready"),
        ("RECORDING_COMPLETED", "Recording Completed"),
        ("TRANSCRIPT_READY", "Transcript Ready"),
        ("TRANSCRIPT_COMPLETED", "Transcript Completed"),
        ("SUMMARY_READY", "Summary Ready"),
        ("SUMMARY_COMPLETED", "Summary Completed"),
        ("YOUTUBE_UPLOAD_COMPLETED", "YouTube Upload Completed"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="webhooks")
    url = models.URLField()
    event = models.CharField(max_length=50, choices=EVENT_CHOICES)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.event} - {self.url}"
