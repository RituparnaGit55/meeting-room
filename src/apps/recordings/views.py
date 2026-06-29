from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from apps.meetings.models import Meeting, MeetingRecording, MeetingParticipant
from .models import Recording
from .serializers import RecordingSerializer


def _get_user_meeting_ids(user):
    """Get meeting IDs where user is host or participant."""
    hosted = Meeting.objects.filter(host=user).values_list('id', flat=True)
    participated = MeetingParticipant.objects.filter(user=user).values_list('meeting_id', flat=True)
    return set(hosted) | set(participated)


class RecordingListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = RecordingSerializer

    def get_queryset(self):
        meeting_ids = _get_user_meeting_ids(self.request.user)
        return Recording.objects.filter(meeting_id__in=meeting_ids)


class RecordingDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = RecordingSerializer

    def get_queryset(self):
        meeting_ids = _get_user_meeting_ids(self.request.user)
        return Recording.objects.filter(meeting_id__in=meeting_ids)


class StartRecordingView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, meeting_id):
        meeting = get_object_or_404(Meeting, pk=meeting_id)
        # Check permissions: only host can toggle recording
        if meeting.host != request.user:
            return Response(
                {"error": "Only the meeting host can start the recording."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        meeting.is_recording = True
        meeting.save()
        return Response(
            {"message": "Recording started.", "is_recording": meeting.is_recording},
            status=status.HTTP_200_OK
        )


class StopRecordingView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, meeting_id):
        meeting = get_object_or_404(Meeting, pk=meeting_id)
        if meeting.host != request.user:
            return Response(
                {"error": "Only the meeting host can stop the recording."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        meeting.is_recording = False
        meeting.save()
        return Response(
            {"message": "Recording stopped.", "is_recording": meeting.is_recording},
            status=status.HTTP_200_OK
        )


class GetRecordingURLView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, meeting_id):
        meeting = get_object_or_404(Meeting, pk=meeting_id)
        
        # Only host or participants can access recording URLs
        is_participant = MeetingParticipant.objects.filter(meeting=meeting, user=request.user).exists()
        if meeting.host != request.user and not is_participant:
            return Response(
                {"error": "You do not have permission to access recordings for this meeting."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Get recordings from both models
        recordings_data = []
        
        # 1. Recording model (apps.recordings)
        for r in Recording.objects.filter(meeting=meeting):
            recordings_data.append({
                "source": "Recording",
                "id": r.id,
                "file_path": r.file_path,
                "file_url": r.file_path, # local path/URL
                "is_uploaded_to_youtube": r.is_uploaded_to_youtube,
                "youtube_url": r.youtube_url,
                "youtube_video_id": r.youtube_video_id,
                "youtube_visibility": r.youtube_visibility,
                "created_at": r.created_at
            })
            
        # 2. MeetingRecording model (apps.meetings)
        for mr in MeetingRecording.objects.filter(meeting=meeting):
            file_url = mr.file.url if mr.file else ""
            if request:
                file_url = request.build_absolute_uri(file_url)
            recordings_data.append({
                "source": "MeetingRecording",
                "id": mr.id,
                "file_path": mr.file.name,
                "file_url": file_url,
                "is_uploaded_to_youtube": mr.is_uploaded_to_youtube,
                "youtube_url": mr.youtube_url,
                "youtube_video_id": mr.youtube_video_id,
                "youtube_visibility": mr.youtube_visibility,
                "created_at": mr.created_at
            })
            
        return Response({
            "meeting_id": meeting.id,
            "meeting_title": meeting.title,
            "recordings": recordings_data
        }, status=status.HTTP_200_OK)
