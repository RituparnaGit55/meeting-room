from django.db import models
from apps.accounts.models import User
from apps.meetings.models import Meeting


class Notification(models.Model):
    TYPE_CHOICES = [
        ("MEETING_INVITE", "Meeting Invite"),
        ("MEETING_START", "Meeting Start"),
        ("MEETING_REMINDER", "Meeting Reminder"),
        ("RECORDING_READY", "Recording Ready"),
        ("TRANSCRIPT_READY", "Transcript Ready"),
        ("SUMMARY_READY", "Summary Ready"),
        ("TASK_ASSIGNED", "Task Assigned"),
        ("YOUTUBE_UPLOADED", "YouTube Upload Complete"),
        ("MESSAGE", "New Message"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications")
    meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE, related_name="notifications", blank=True, null=True)
    type = models.CharField(max_length=50, choices=TYPE_CHOICES)
    title = models.CharField(max_length=255)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} - {self.user.email}"
