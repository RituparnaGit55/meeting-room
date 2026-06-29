from django.db import models
from apps.accounts.models import User
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


class MeetingNote(models.Model):
    NOTE_TYPES = [
        ("NOTE", "Note"),
        ("HIGHLIGHT", "Discussion Highlight"),
        ("QUESTION", "Question"),
    ]

    meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE, related_name="meeting_notes")
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="meeting_notes")
    content = models.TextField()
    note_type = models.CharField(max_length=20, choices=NOTE_TYPES, default="NOTE")
    is_resolved = models.BooleanField(default=False, help_text="For questions - marks if answered")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.get_note_type_display()}: {self.content[:50]}"
