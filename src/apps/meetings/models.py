import secrets
from django.db import models
from django.utils import timezone
from apps.accounts.models import User


class Meeting(models.Model):
    TYPE_CHOICES = [
        ("INSTANT", "Instant Meeting"),
        ("SCHEDULED", "Scheduled Meeting"),
        ("RECURRING", "Recurring Meeting"),
        ("LINK_GENERATION", "Meeting Link Generation"),
        ("ID_GENERATION", "Meeting ID Generation"),
    ]
    STATUS_CHOICES = [
        ("SCHEDULED", "Scheduled"),
        ("IN_PROGRESS", "In Progress"),
        ("COMPLETED", "Completed"),
        ("CANCELLED", "Cancelled"),
    ]
    RECURRENCE_CHOICES = [
        ("NONE", "None"),
        ("DAILY", "Daily"),
        ("WEEKLY", "Weekly"),
        ("MONTHLY", "Monthly"),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    meeting_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default="SCHEDULED")
    host = models.ForeignKey(User, on_delete=models.CASCADE, related_name="hosted_meetings")
    room_code = models.CharField(max_length=12, unique=True, editable=False)
    meeting_id = models.CharField(max_length=20, unique=True, editable=False)
    password = models.CharField(max_length=20, blank=True, null=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(blank=True, null=True)
    duration = models.IntegerField(help_text="Duration in minutes", blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="SCHEDULED")
    is_recording = models.BooleanField(default=False)
    enable_waiting_room = models.BooleanField(default=False)
    recurrence_pattern = models.CharField(max_length=20, choices=RECURRENCE_CHOICES, default="NONE")
    recurrence_end_date = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.room_code:
            self.room_code = secrets.token_hex(6).upper()
        if not self.meeting_id:
            self.meeting_id = secrets.token_urlsafe(12)
        if self.start_time and self.duration and not self.end_time:
            self.end_time = self.start_time + timezone.timedelta(minutes=self.duration)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} ({self.room_code})"


class MeetingParticipant(models.Model):
    ROLE_CHOICES = [
        ("HOST", "Host"),
        ("CO_HOST", "Co-Host"),
        ("PARTICIPANT", "Participant"),
        ("GUEST", "Guest"),
    ]
    STATUS_CHOICES = [
        ("WAITING", "Waiting Room"),
        ("JOINED", "Joined"),
        ("LEFT", "Left"),
        ("REMOVED", "Removed"),
    ]

    meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE, related_name="participants")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="participated_meetings", blank=True, null=True)
    guest_name = models.CharField(max_length=255, blank=True, null=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="PARTICIPANT")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="JOINED")
    joined_at = models.DateTimeField(auto_now_add=True)
    left_at = models.DateTimeField(blank=True, null=True)
    is_screen_sharing = models.BooleanField(default=False)
    is_video_on = models.BooleanField(default=True)
    is_audio_on = models.BooleanField(default=True)
    has_raised_hand = models.BooleanField(default=False)
    hand_raised_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        unique_together = ["meeting", "user"]
        ordering = ["-joined_at"]

    def __str__(self):
        if self.user:
            return f"{self.user.email} - {self.meeting.title}"
        return f"{self.guest_name} - {self.meeting.title}"


class MeetingRecording(models.Model):
    VISIBILITY_CHOICES = [
        ("private", "Private"),
        ("unlisted", "Unlisted"),
        ("public", "Public"),
    ]

    meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE, related_name="meeting_recordings")
    started_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    file = models.FileField(upload_to="meeting_recordings/")
    recording_type = models.CharField(max_length=20)  # e.g., 'video', 'audio', 'screen'
    file_size = models.BigIntegerField(null=True, blank=True)
    is_uploaded_to_youtube = models.BooleanField(default=False)
    youtube_url = models.URLField(blank=True, null=True)
    youtube_video_id = models.CharField(max_length=100, blank=True, null=True)
    youtube_visibility = models.CharField(
        max_length=20, choices=VISIBILITY_CHOICES, default="private", blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Recording ({self.recording_type}) for {self.meeting.title} at {self.created_at}"
