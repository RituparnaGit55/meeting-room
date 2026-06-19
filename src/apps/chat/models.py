from django.db import models
from ..accounts.models import User
from ..meetings.models import Meeting


class Message(models.Model):
    FILE_TYPES = [
        ("image", "Image"),
        ("video", "Video"),
        ("document", "Document"),
    ]

    meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE, related_name="messages")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="messages", null=True, blank=True)
    sender_name = models.CharField(max_length=255, blank=True, null=True)
    
    # For private messaging
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name="received_messages", null=True, blank=True)
    is_private = models.BooleanField(default=False)
    
    content = models.TextField(blank=True, null=True)
    
    # For file attachments
    attachment = models.FileField(upload_to="chat_attachments/", blank=True, null=True)
    file_type = models.CharField(max_length=20, choices=FILE_TYPES, blank=True, null=True)
    file_name = models.CharField(max_length=255, blank=True, null=True)

    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["timestamp"]

    def __str__(self):
        sender = self.user.email if self.user else self.sender_name
        return f"{sender} - {self.timestamp}"
