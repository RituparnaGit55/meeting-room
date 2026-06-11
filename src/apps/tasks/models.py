from django.db import models
from apps.accounts.models import User
from apps.meetings.models import Meeting


class Task(models.Model):
    STATUS_CHOICES = [
        ("TODO", "To Do"),
        ("IN_PROGRESS", "In Progress"),
        ("DONE", "Done"),
    ]

    meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE, related_name="tasks", blank=True, null=True)
    assignee = models.ForeignKey(User, on_delete=models.CASCADE, related_name="assigned_tasks")
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name="created_tasks")
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    due_date = models.DateTimeField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="TODO")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
