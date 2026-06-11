from django.db import models
from apps.accounts.models import User
from apps.meetings.models import Meeting


class Transcript(models.Model):
    meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE, related_name="transcripts")
    speaker = models.ForeignKey(User, on_delete=models.CASCADE, related_name="transcripts", blank=True, null=True)
    text = models.TextField()
    start_time = models.FloatField(blank=True, null=True)
    end_time = models.FloatField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Transcript for {self.meeting.title} at {self.created_at}"
