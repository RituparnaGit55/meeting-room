from django.db import models
from apps.accounts.models import User
from apps.meetings.models import Meeting


class MeetingAnalytics(models.Model):
    meeting = models.OneToOneField(Meeting, on_delete=models.CASCADE, related_name="analytics")
    total_participants = models.IntegerField(default=0)
    average_attendance_time = models.FloatField(blank=True, null=True)
    total_messages = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Analytics for {self.meeting.title}"


class UserAnalytics(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="analytics")
    total_meetings_hosted = models.IntegerField(default=0)
    total_meetings_attended = models.IntegerField(default=0)
    total_tasks_completed = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Analytics for {self.user.email}"
