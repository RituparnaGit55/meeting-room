from django.core.management.base import BaseCommand
from apps.notifications.reminder_service import MeetingReminderService


class Command(BaseCommand):
    help = "Send meeting reminder notifications for meetings starting within 15 minutes."

    def handle(self, *args, **options):
        self.stdout.write("Checking for upcoming meetings...")
        sent_count = MeetingReminderService.send_due_reminders()
        if sent_count:
            self.stdout.write(
                self.style.SUCCESS(f"Sent {sent_count} meeting reminder(s).")
            )
        else:
            self.stdout.write("No reminders to send at this time.")
