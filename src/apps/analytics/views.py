from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count, Sum, Avg
from apps.accounts.permissions import IsAdmin, IsManager
from apps.meetings.models import Meeting, MeetingParticipant, MeetingRecording
from apps.recordings.models import Recording
from .models import MeetingAnalytics, UserAnalytics
from .serializers import MeetingAnalyticsSerializer, UserAnalyticsSerializer


class MeetingAnalyticsListCreateView(generics.ListCreateAPIView):
    """Admin/Manager only — system-wide meeting analytics."""
    permission_classes = [IsManager]
    serializer_class = MeetingAnalyticsSerializer
    queryset = MeetingAnalytics.objects.all()


class MeetingAnalyticsDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Admin/Manager only — system-wide meeting analytics detail."""
    permission_classes = [IsManager]
    serializer_class = MeetingAnalyticsSerializer
    queryset = MeetingAnalytics.objects.all()


class UserAnalyticsListCreateView(generics.ListCreateAPIView):
    """Admin only — user analytics across all users."""
    permission_classes = [IsAdmin]
    serializer_class = UserAnalyticsSerializer
    queryset = UserAnalytics.objects.all()


class UserAnalyticsDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Admin only — user analytics detail."""
    permission_classes = [IsAdmin]
    serializer_class = UserAnalyticsSerializer
    queryset = UserAnalytics.objects.all()


class MeetingStatisticsView(APIView):
    """User-scoped meeting statistics (own meetings only)."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        # Filter meetings hosted or attended by user
        meetings = Meeting.objects.filter(host=user) | Meeting.objects.filter(participants__user=user)
        meetings = meetings.distinct()

        total_meetings = meetings.count()
        
        # Breakdown by status
        status_breakdown = meetings.values('status').annotate(count=Count('id'))
        
        # Breakdown by type
        type_breakdown = meetings.values('meeting_type').annotate(count=Count('id'))
        
        # Durations
        durations = meetings.filter(duration__isnull=False)
        total_duration = durations.aggregate(total=Sum('duration'))['total'] or 0
        avg_duration = durations.aggregate(avg=Avg('duration'))['avg'] or 0.0

        return Response({
            "total_meetings": total_meetings,
            "total_duration_minutes": total_duration,
            "average_duration_minutes": round(avg_duration, 1),
            "status_breakdown": {item['status']: item['count'] for item in status_breakdown},
            "type_breakdown": {item['meeting_type']: item['count'] for item in type_breakdown}
        }, status=status.HTTP_200_OK)


class AttendanceStatisticsView(APIView):
    """User-scoped attendance statistics (own meetings only)."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        meetings = Meeting.objects.filter(host=user) | Meeting.objects.filter(participants__user=user)
        meetings = meetings.distinct()

        meeting_ids = meetings.values_list('id', flat=True)
        participants = MeetingParticipant.objects.filter(meeting_id__in=meeting_ids)

        total_participants_records = participants.count()
        avg_participants_per_meeting = total_participants_records / len(meeting_ids) if len(meeting_ids) > 0 else 0.0
        
        # Breakdown by role
        role_breakdown = participants.values('role').annotate(count=Count('id'))
        
        # Breakdown by status (WAITING, JOINED, LEFT, REMOVED)
        status_breakdown = participants.values('status').annotate(count=Count('id'))

        return Response({
            "total_attendance_records": total_participants_records,
            "average_participants_per_meeting": round(avg_participants_per_meeting, 1),
            "role_breakdown": {item['role']: item['count'] for item in role_breakdown},
            "status_breakdown": {item['status']: item['count'] for item in status_breakdown}
        }, status=status.HTTP_200_OK)


class RecordingStatisticsView(APIView):
    """User-scoped recording statistics (own meetings only)."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        meetings = Meeting.objects.filter(host=user) | Meeting.objects.filter(participants__user=user)
        meetings = meetings.distinct()

        meeting_ids = meetings.values_list('id', flat=True)
        
        # 1. Recording model metrics
        recordings = Recording.objects.filter(meeting_id__in=meeting_ids)
        total_recordings_count = recordings.count()
        total_recordings_size = recordings.aggregate(total_size=Sum('file_size'))['total_size'] or 0
        youtube_uploaded_count = recordings.filter(is_uploaded_to_youtube=True).count()

        # 2. MeetingRecording model metrics
        meeting_recordings = MeetingRecording.objects.filter(meeting_id__in=meeting_ids)
        total_meeting_recordings_count = meeting_recordings.count()
        total_meeting_recordings_size = meeting_recordings.aggregate(total_size=Sum('file_size'))['total_size'] or 0
        youtube_uploaded_meeting_count = meeting_recordings.filter(is_uploaded_to_youtube=True).count()

        # Aggregated
        grand_total_count = total_recordings_count + total_meeting_recordings_count
        grand_total_size_bytes = total_recordings_size + total_meeting_recordings_size
        grand_total_uploaded_youtube = youtube_uploaded_count + youtube_uploaded_meeting_count
        
        # Breakdown by type
        type_breakdown = {
            "video": meeting_recordings.filter(recording_type="video").count() + total_recordings_count,
            "audio": meeting_recordings.filter(recording_type="audio").count(),
            "screen": meeting_recordings.filter(recording_type="screen").count()
        }

        youtube_success_rate = (grand_total_uploaded_youtube / grand_total_count * 100) if grand_total_count > 0 else 0.0

        return Response({
            "total_recordings": grand_total_count,
            "total_file_size_bytes": grand_total_size_bytes,
            "youtube_uploaded_count": grand_total_uploaded_youtube,
            "youtube_success_rate_percent": round(youtube_success_rate, 1),
            "type_breakdown": type_breakdown
        }, status=status.HTTP_200_OK)
