from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from apps.meetings.models import Meeting, MeetingParticipant
from .models import Summary, MeetingNote
from .serializers import SummarySerializer, MeetingNoteSerializer
from .tasks import generate_meeting_summary


def _get_user_meeting_ids(user):
    """Get meeting IDs where user is host or participant."""
    hosted = Meeting.objects.filter(host=user).values_list('id', flat=True)
    participated = MeetingParticipant.objects.filter(user=user).values_list('meeting_id', flat=True)
    return set(hosted) | set(participated)


class SummaryListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = SummarySerializer

    def get_queryset(self):
        meeting_ids = _get_user_meeting_ids(self.request.user)
        return Summary.objects.filter(meeting_id__in=meeting_ids)


class SummaryDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = SummarySerializer

    def get_queryset(self):
        meeting_ids = _get_user_meeting_ids(self.request.user)
        return Summary.objects.filter(meeting_id__in=meeting_ids)


class MeetingSummaryRetrieveView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = SummarySerializer
    lookup_field = 'meeting_id'

    def get_queryset(self):
        meeting_ids = _get_user_meeting_ids(self.request.user)
        return Summary.objects.filter(meeting_id__in=meeting_ids)


class GenerateSummaryView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, meeting_id):
        meeting = get_object_or_404(Meeting, pk=meeting_id)
        
        # Only host or participants can generate summaries
        is_participant = MeetingParticipant.objects.filter(meeting=meeting, user=request.user).exists()
        if meeting.host != request.user and not is_participant:
            return Response(
                {"error": "You do not have permission to generate a summary for this meeting."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        generate_meeting_summary.delay(meeting_id)
        return Response(
            {"message": "Summary generation triggered successfully."},
            status=status.HTTP_202_ACCEPTED
        )


# ============ Meeting Notes (Real-Time) ============

class MeetingNoteListCreateView(generics.ListCreateAPIView):
    """List and create notes for a specific meeting."""
    permission_classes = [IsAuthenticated]
    serializer_class = MeetingNoteSerializer

    def get_queryset(self):
        meeting_id = self.kwargs.get("meeting_id")
        # Verify user is a participant of this meeting
        meeting_ids = _get_user_meeting_ids(self.request.user)
        if int(meeting_id) not in meeting_ids:
            return MeetingNote.objects.none()
        note_type = self.request.query_params.get("type")
        qs = MeetingNote.objects.filter(meeting_id=meeting_id)
        if note_type:
            qs = qs.filter(note_type=note_type.upper())
        return qs

    def perform_create(self, serializer):
        serializer.save(
            author=self.request.user if self.request.user.is_authenticated else None,
            meeting_id=self.kwargs.get("meeting_id"),
        )


class MeetingNoteDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Update or delete a specific meeting note."""
    permission_classes = [IsAuthenticated]
    serializer_class = MeetingNoteSerializer

    def get_queryset(self):
        meeting_ids = _get_user_meeting_ids(self.request.user)
        return MeetingNote.objects.filter(meeting_id__in=meeting_ids)
