from django.db import models
from apps.meetings.models import Meeting


class Summary(models.Model):
    meeting = models.OneToOneField(Meeting, on_delete=models.CASCADE, related_name="summary")
    summary_text = models.TextField(blank=True, null=True)
    key_points = models.JSONField(default=list, blank=True)
    decisions_taken = models.JSONField(default=list, blank=True)
    action_items = models.JSONField(default=list, blank=True)
    follow_up_tasks = models.JSONField(default=list, blank=True)
    meeting_notes = models.TextField(blank=True, null=True)
    minutes_of_meeting = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Summary for {self.meeting.title}"
