import json
from celery import shared_task
from django.conf import settings
from openai import OpenAI
from apps.meetings.models import Meeting
from apps.summaries.models import Summary
from .models import Task


@shared_task
def generate_tasks_from_summary(meeting_id):
    """
    After a meeting summary is generated, use OpenAI to parse action items
    and follow-up tasks into structured Task objects.
    """
    try:
        meeting = Meeting.objects.get(id=meeting_id)
        try:
            summary = Summary.objects.get(meeting=meeting)
        except Summary.DoesNotExist:
            print(f"No summary found for meeting {meeting_id}. Cannot generate tasks.")
            return

        action_items = summary.action_items or []
        follow_up_tasks = summary.follow_up_tasks or []
        all_items = action_items + follow_up_tasks

        if not all_items:
            print(f"No action items or follow-up tasks for meeting {meeting_id}.")
            return

        # Get meeting participants to match assignees
        from apps.accounts.models import User
        participants = meeting.participants.filter(user__isnull=False).select_related("user")
        participant_names = []
        for p in participants:
            name = p.user.get_full_name() or p.user.email
            participant_names.append({"name": name, "user_id": p.user.id})

        if not settings.OPENAI_API_KEY:
            # Fallback: create tasks without assignees
            for item in all_items:
                Task.objects.get_or_create(
                    meeting=meeting,
                    title=item[:255],
                    defaults={
                        "description": item,
                        "creator": meeting.host,
                        "assignee": meeting.host,
                        "status": "TODO",
                    }
                )
            print(f"Created {len(all_items)} tasks (no AI assignee matching) for meeting {meeting_id}.")

            # Send task assignment notifications
            _send_task_notifications(meeting)
            return

        client = OpenAI(api_key=settings.OPENAI_API_KEY)

        system_prompt = f"""You are an assistant that maps action items to team members.
Given a list of action items and a list of participants, output a JSON array where each element has:
- "title": short task title (max 200 chars)
- "description": the full action item text
- "assignee_user_id": the user_id of the most likely assignee from the participants list, or null if unclear
- "due_days": estimated number of days to complete (integer, default 7)

Participants: {json.dumps(participant_names)}
"""

        items_text = "\n".join([f"- {item}" for item in all_items])

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Map these action items to participants:\n{items_text}\n\nReturn a JSON object with key \"tasks\" containing the array."}
            ]
        )

        content = response.choices[0].message.content
        parsed = json.loads(content)
        task_list = parsed.get("tasks", [])

        from django.utils import timezone
        created_count = 0
        for task_data in task_list:
            assignee_id = task_data.get("assignee_user_id")
            assignee = None
            if assignee_id:
                try:
                    assignee = User.objects.get(id=assignee_id)
                except User.DoesNotExist:
                    assignee = meeting.host
            else:
                assignee = meeting.host

            due_days = task_data.get("due_days", 7)
            Task.objects.get_or_create(
                meeting=meeting,
                title=task_data.get("title", "Untitled Task")[:255],
                defaults={
                    "description": task_data.get("description", ""),
                    "creator": meeting.host,
                    "assignee": assignee,
                    "due_date": timezone.now() + timezone.timedelta(days=due_days),
                    "status": "TODO",
                }
            )
            created_count += 1

        print(f"Created {created_count} tasks for meeting {meeting_id}.")

        # Send task assignment notifications
        _send_task_notifications(meeting)

    except Exception as e:
        print(f"Error generating tasks for meeting {meeting_id}: {e}")


def _send_task_notifications(meeting):
    """Send notifications to task assignees."""
    try:
        from apps.notifications.services import NotificationService
        tasks = Task.objects.filter(meeting=meeting)
        for task in tasks:
            NotificationService.create_notification(
                user=task.assignee,
                notification_type="TASK_ASSIGNED",
                title=f"New Task: {task.title}",
                message=f"You have been assigned a task from meeting '{meeting.title}': {task.title}",
                meeting=meeting,
            )
    except Exception as e:
        print(f"Error sending task notifications: {e}")
