from django.utils import timezone
from datetime import timedelta

from apps.meetings.models import Meeting
from .models import Notification
from .services import NotificationService


class MeetingReminderService:
    """
    Service for sending meeting reminder notifications to hosts and participants.
    Designed to be called periodically (e.g. every 5 minutes via cron or management command).
    """

    REMINDER_WINDOW_MINUTES = 15

    @classmethod
    def send_due_reminders(cls):
        """
        Find meetings starting within the next REMINDER_WINDOW_MINUTES that
        haven't had participant reminders sent yet, and send them.
        """
        now = timezone.now()
        window_end = now + timedelta(minutes=cls.REMINDER_WINDOW_MINUTES)

        # Find scheduled meetings starting within the window
        upcoming_meetings = Meeting.objects.filter(
            status="SCHEDULED",
            start_time__gte=now,
            start_time__lte=window_end,
        )

        sent_count = 0
        for meeting in upcoming_meetings:
            sent_count += cls._send_reminder_for_meeting(meeting)

        return sent_count

    @classmethod
    def _send_reminder_for_meeting(cls, meeting):
        """Send reminders to all participants of a meeting if not already sent."""
        sent = 0

        # Get all participants with user accounts
        participants = meeting.participants.filter(
            user__isnull=False,
        ).select_related("user")

        time_str = meeting.start_time.strftime("%I:%M %p")
        title = f"Meeting Starting Soon: {meeting.title}"
        message = (
            f"Your meeting '{meeting.title}' starts at {time_str}. "
            f"Room code: {meeting.room_code}"
        )

        for participant in participants:
            # Check if we already sent a reminder to this user for this meeting
            already_reminded = Notification.objects.filter(
                user=participant.user,
                meeting=meeting,
                type="MEETING_REMINDER",
                title__startswith="Meeting Starting Soon:",
            ).exists()

            if not already_reminded:
                NotificationService.create_notification(
                    user=participant.user,
                    notification_type="MEETING_REMINDER",
                    title=title,
                    message=message,
                    meeting=meeting,
                )
                sent += 1

        # Also ensure host gets a reminder
        host_reminded = Notification.objects.filter(
            user=meeting.host,
            meeting=meeting,
            type="MEETING_REMINDER",
            title__startswith="Meeting Starting Soon:",
        ).exists()

        if not host_reminded:
            NotificationService.create_notification(
                user=meeting.host,
                notification_type="MEETING_REMINDER",
                title=title,
                message=message,
                meeting=meeting,
            )
            sent += 1

        return sent
