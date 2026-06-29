from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from apps.meetings.models import Meeting, MeetingRecording, MeetingParticipant
from apps.recordings.models import Recording
from .models import Transcript
from .serializers import TranscriptSerializer


def _get_user_meeting_ids(user):
    """Get meeting IDs where user is host or participant."""
    hosted = Meeting.objects.filter(host=user).values_list('id', flat=True)
    participated = MeetingParticipant.objects.filter(user=user).values_list('meeting_id', flat=True)
    return set(hosted) | set(participated)


class TranscriptListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TranscriptSerializer

    def get_queryset(self):
        meeting_ids = _get_user_meeting_ids(self.request.user)
        return Transcript.objects.filter(meeting_id__in=meeting_ids)


class TranscriptDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TranscriptSerializer

    def get_queryset(self):
        meeting_ids = _get_user_meeting_ids(self.request.user)
        return Transcript.objects.filter(meeting_id__in=meeting_ids)


class MeetingTranscriptListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TranscriptSerializer

    def get_queryset(self):
        meeting_id = self.kwargs.get('meeting_id')
        # Verify user is a participant of this meeting
        meeting_ids = _get_user_meeting_ids(self.request.user)
        if int(meeting_id) not in meeting_ids:
            return Transcript.objects.none()
        return Transcript.objects.filter(meeting_id=meeting_id).order_by('start_time')


class GenerateTranscriptView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, meeting_id):
        meeting = get_object_or_404(Meeting, pk=meeting_id)
        
        # Check permissions: only host or participants
        is_participant = MeetingParticipant.objects.filter(meeting=meeting, user=request.user).exists()
        if meeting.host != request.user and not is_participant:
            return Response(
                {"error": "You do not have permission to trigger transcription for this meeting."},
                status=status.HTTP_403_FORBIDDEN
            )
            
        recordings = Recording.objects.filter(meeting=meeting)
        meeting_recordings = MeetingRecording.objects.filter(meeting=meeting)
        
        if not recordings.exists() and not meeting_recordings.exists():
            return Response(
                {"error": "No recordings found for this meeting to transcribe."},
                status=status.HTTP_404_NOT_FOUND
            )
            
        from apps.transcripts.tasks import process_transcription
        
        triggered_count = 0
        for r in recordings:
            process_transcription.delay(r.id, "Recording")
            triggered_count += 1
        for mr in meeting_recordings:
            process_transcription.delay(mr.id, "MeetingRecording")
            triggered_count += 1
            
        return Response(
            {"message": f"Transcription task triggered for {triggered_count} recording(s)."},
            status=status.HTTP_202_ACCEPTED
        )
