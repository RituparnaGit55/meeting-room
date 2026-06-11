from django.db import models
from apps.accounts.models import User
from apps.meetings.models import Meeting


class Message(models.Model):
    meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE, related_name="messages")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="messages")
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} - {self.timestamp}"
