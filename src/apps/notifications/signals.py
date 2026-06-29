from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

from apps.meetings.models import Meeting
from apps.tasks.models import Task


@receiver(post_save, sender=Meeting)
def schedule_meeting_reminder(sender, instance, created, **kwargs):
    """
    When a scheduled meeting is created with a future start_time,
    pre-create a MEETING_REMINDER notification for the host.
    The reminder_service will handle notifying participants closer to the time.
    """
    if not created:
        return

    if instance.start_time and instance.start_time > timezone.now():
        from .services import NotificationService

        NotificationService.create_notification(
            user=instance.host,
            notification_type="MEETING_REMINDER",
            title=f"Upcoming: {instance.title}",
            message=(
                f"Your meeting '{instance.title}' is scheduled for "
                f"{instance.start_time.strftime('%b %d, %Y at %I:%M %p')}."
            ),
            meeting=instance,
        )


@receiver(post_save, sender=Task)
def notify_task_assignee(sender, instance, created, **kwargs):
    """
    Safety-net signal: when a Task is created, notify the assignee.
    Checks for existing notification to avoid duplicates with the inline
    call in tasks/tasks.py.
    """
    if not created:
        return

    from .models import Notification
    from .services import NotificationService

    # Skip if a TASK_ASSIGNED notification already exists for this user + meeting combo
    already_notified = Notification.objects.filter(
        user=instance.assignee,
        meeting=instance.meeting,
        type="TASK_ASSIGNED",
        title__contains=instance.title[:100],
    ).exists()

    if not already_notified:
        NotificationService.create_notification(
            user=instance.assignee,
            notification_type="TASK_ASSIGNED",
            title=f"New Task: {instance.title}",
            message=(
                f"You have been assigned a task: {instance.title}"
                + (f" from meeting '{instance.meeting.title}'" if instance.meeting else "")
            ),
            meeting=instance.meeting,
        )
