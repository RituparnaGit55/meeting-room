from .models import Notification


class NotificationService:
    """Centralized service for creating notifications across the pipeline."""

    @staticmethod
    def create_notification(user, notification_type, title, message, meeting=None):
        """Create a notification for a user."""
        if not user:
            return None
        return Notification.objects.create(
            user=user,
            meeting=meeting,
            type=notification_type,
            title=title,
            message=message,
        )

    @staticmethod
    def notify_meeting_participants(meeting, notification_type, title, message, exclude_user=None):
        """Send a notification to all participants of a meeting."""
        participants = meeting.participants.filter(
            user__isnull=False, status="JOINED"
        ).select_related("user")
        notifications = []
        for participant in participants:
            if exclude_user and participant.user == exclude_user:
                continue
            notifications.append(
                Notification(
                    user=participant.user,
                    meeting=meeting,
                    type=notification_type,
                    title=title,
                    message=message,
                )
            )
        if notifications:
            Notification.objects.bulk_create(notifications)
        return notifications

    @staticmethod
    def notify_host(meeting, notification_type, title, message):
        """Send a notification to the meeting host."""
        return NotificationService.create_notification(
            user=meeting.host,
            notification_type=notification_type,
            title=title,
            message=message,
            meeting=meeting,
        )

    @staticmethod
    def notify_all_participants(meeting, notification_type, title, message):
        """
        Send a notification to ALL participants of a meeting, including the host.
        Used for meeting reminders.
        """
        participants = meeting.participants.filter(
            user__isnull=False,
        ).select_related("user")

        notified_user_ids = set()
        notifications = []

        for participant in participants:
            if participant.user_id not in notified_user_ids:
                notifications.append(
                    Notification(
                        user=participant.user,
                        meeting=meeting,
                        type=notification_type,
                        title=title,
                        message=message,
                    )
                )
                notified_user_ids.add(participant.user_id)

        # Also ensure the host is notified
        if meeting.host_id not in notified_user_ids:
            notifications.append(
                Notification(
                    user=meeting.host,
                    meeting=meeting,
                    type=notification_type,
                    title=title,
                    message=message,
                )
            )

        if notifications:
            Notification.objects.bulk_create(notifications)
        return notifications

    @staticmethod
    def get_user_notifications(user, unread_only=False, limit=None):
        """Get notifications for a user, optionally filtered."""
        qs = Notification.objects.filter(user=user)
        if unread_only:
            qs = qs.filter(is_read=False)
        if limit:
            qs = qs[:limit]
        return qs

    @staticmethod
    def get_unread_count(user):
        """Get the count of unread notifications for a user."""
        return Notification.objects.filter(user=user, is_read=False).count()
