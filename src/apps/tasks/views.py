from django.db.models import Q
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from apps.meetings.models import Meeting, MeetingParticipant
from .models import Task
from .serializers import TaskSerializer


def _get_user_meeting_ids(user):
    """Get meeting IDs where user is host or participant."""
    hosted = Meeting.objects.filter(host=user).values_list('id', flat=True)
    participated = MeetingParticipant.objects.filter(user=user).values_list('meeting_id', flat=True)
    return set(hosted) | set(participated)


class TaskListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TaskSerializer

    def get_queryset(self):
        user = self.request.user
        meeting_ids = _get_user_meeting_ids(user)
        # User can see tasks they are assigned, created, or from their meetings
        qs = Task.objects.filter(
            Q(assignee=user) | Q(creator=user) | Q(meeting_id__in=meeting_ids)
        ).distinct()
        # Filter by assignee (my tasks)
        if self.request.query_params.get("my_tasks") == "true":
            qs = qs.filter(assignee=user)
        return qs


class TaskDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TaskSerializer

    def get_queryset(self):
        user = self.request.user
        meeting_ids = _get_user_meeting_ids(user)
        return Task.objects.filter(
            Q(assignee=user) | Q(creator=user) | Q(meeting_id__in=meeting_ids)
        ).distinct()


class MeetingTaskListView(generics.ListAPIView):
    """List all tasks generated from a specific meeting."""
    permission_classes = [IsAuthenticated]
    serializer_class = TaskSerializer

    def get_queryset(self):
        meeting_id = self.kwargs.get("meeting_id")
        # Verify user is a participant
        meeting_ids = _get_user_meeting_ids(self.request.user)
        if int(meeting_id) not in meeting_ids:
            return Task.objects.none()
        return Task.objects.filter(meeting_id=meeting_id).order_by("-created_at")
