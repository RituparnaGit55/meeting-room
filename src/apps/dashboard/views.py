from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import TemplateView
from django.db.models import Sum
from apps.meetings.models import Meeting, MeetingParticipant, MeetingRecording
from apps.recordings.models import Recording
from apps.transcripts.models import Transcript
from apps.summaries.models import Summary
from apps.accounts.models import User


class AdminRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        request = getattr(self, "request", None)
        if request and request.user and request.user.is_authenticated:
            return (
                getattr(request.user, 'role', None) == 'ADMIN'
                or request.user.is_superuser
                or request.user.is_staff
            )
        return False

    def handle_no_permission(self):
        """Redirect non-admin users to user dashboard instead of 403."""
        from django.shortcuts import redirect
        request = getattr(self, "request", None)
        if request and request.user and request.user.is_authenticated:
            return redirect("meeting-dashboard")
        return super().handle_no_permission()


class AdminDashboardPageView(AdminRequiredMixin, TemplateView):
    template_name = "dashboard/admin_dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Total counts
        context["total_meetings"] = Meeting.objects.count()
        context["total_participants"] = MeetingParticipant.objects.count()
        
        total_rec_model = Recording.objects.count()
        total_meet_rec_model = MeetingRecording.objects.count()
        context["total_recordings"] = total_rec_model + total_meet_rec_model
        
        context["total_transcripts"] = Transcript.objects.count()
        context["ai_summary_usage"] = Summary.objects.count()
        
        # Storage Stats
        rec_size = Recording.objects.aggregate(Sum('file_size'))['file_size__sum'] or 0
        meet_rec_size = MeetingRecording.objects.aggregate(Sum('file_size'))['file_size__sum'] or 0
        total_size_bytes = rec_size + meet_rec_size
        
        # Format size
        total_size_mb = total_size_bytes / (1024 * 1024)
        if total_size_mb > 1024:
            context["storage_stats_display"] = f"{total_size_mb / 1024:.2f} GB"
        else:
            context["storage_stats_display"] = f"{total_size_mb:.2f} MB"
            
        # API Usage
        context["api_assemblyai_calls"] = context["total_recordings"]  # Every recording triggers transcription
        context["api_openai_calls"] = context["ai_summary_usage"]       # Every summary triggers OpenAI
        
        yt_rec = Recording.objects.filter(is_uploaded_to_youtube=True).count()
        yt_meet = MeetingRecording.objects.filter(is_uploaded_to_youtube=True).count()
        context["api_youtube_uploads"] = yt_rec + yt_meet
        
        context["total_users"] = User.objects.count()
        context["active_users"] = User.objects.filter(is_active=True).count()
        
        return context


class DashboardView(APIView):
    """Admin-only API endpoint for dashboard statistics."""
    def get_permissions(self):
        from apps.accounts.permissions import IsAdmin
        return [IsAdmin()]

    def get(self, request):
        total_meetings = Meeting.objects.count()
        total_participants = MeetingParticipant.objects.count()
        
        rec_size = Recording.objects.aggregate(Sum('file_size'))['file_size__sum'] or 0
        meet_rec_size = MeetingRecording.objects.aggregate(Sum('file_size'))['file_size__sum'] or 0
        total_size_bytes = rec_size + meet_rec_size
        
        yt_rec = Recording.objects.filter(is_uploaded_to_youtube=True).count()
        yt_meet = MeetingRecording.objects.filter(is_uploaded_to_youtube=True).count()
        
        return Response({
            "total_meetings": total_meetings,
            "total_participants": total_participants,
            "total_recordings": Recording.objects.count() + MeetingRecording.objects.count(),
            "total_transcripts": Transcript.objects.count(),
            "ai_summary_usage": Summary.objects.count(),
            "storage_size_bytes": total_size_bytes,
            "api_usage": {
                "assemblyai_calls": Recording.objects.count() + MeetingRecording.objects.count(),
                "openai_calls": Summary.objects.count(),
                "youtube_uploads": yt_rec + yt_meet
            }
        })
