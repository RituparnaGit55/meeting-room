from django.db import models
from apps.meetings.models import Meeting


class Recording(models.Model):
    meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE, related_name="recordings")
    file_path = models.CharField(max_length=500)
    file_size = models.BigIntegerField(blank=True, null=True)
    duration = models.IntegerField(blank=True, null=True)
    is_uploaded_to_youtube = models.BooleanField(default=False)
    youtube_url = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Recording for {self.meeting.title}"
