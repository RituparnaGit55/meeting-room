import csv
from django.http import HttpResponse, JsonResponse
from django.views import View
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import TemplateView
from django.db.models import Sum, Count
from django.shortcuts import get_object_or_404, redirect

from apps.meetings.models import Meeting, MeetingParticipant, MeetingRecording
from apps.recordings.models import Recording
from apps.transcripts.models import Transcript
from apps.summaries.models import Summary
from apps.accounts.models import User


class AdminRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    login_url = "/auth/admin-login/"

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
        request = getattr(self, "request", None)
        if request and request.user and request.user.is_authenticated:
            return redirect("my-meetings")
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
        
        total_size_mb = total_size_bytes / (1024 * 1024)
        if total_size_mb > 1024:
            context["storage_stats_display"] = f"{total_size_mb / 1024:.2f} GB"
        else:
            context["storage_stats_display"] = f"{total_size_mb:.2f} MB"
            
        # API Usage
        context["api_assemblyai_calls"] = context["total_recordings"]
        context["api_openai_calls"] = context["ai_summary_usage"]
        
        yt_rec = Recording.objects.filter(is_uploaded_to_youtube=True).count()
        yt_meet = MeetingRecording.objects.filter(is_uploaded_to_youtube=True).count()
        context["api_youtube_uploads"] = yt_rec + yt_meet
        
        context["total_users"] = User.objects.count()
        context["active_users"] = User.objects.filter(is_active=True).count()
        context["admin_users_count"] = User.objects.filter(role="ADMIN").count()
        
        # Data Lists for Management Tables
        context["users_list"] = User.objects.annotate(
            hosted_count=Count('hosted_meetings', distinct=True)
        ).order_by('-created_at')
        
        context["meetings_list"] = Meeting.objects.select_related('host').annotate(
            participant_count=Count('participants', distinct=True)
        ).order_by('-created_at')
        
        context["active_rooms"] = Meeting.objects.filter(
            status__in=['IN_PROGRESS', 'SCHEDULED']
        ).select_related('host').annotate(
            joined_participants=Count('participants', distinct=True)
        ).order_by('-start_time')
        
        context["recordings_list"] = Recording.objects.select_related('user').order_by('-created_at')[:20]
        context["transcripts_list"] = Transcript.objects.select_related('meeting').order_by('-created_at')[:20]
        
        return context


class AdminUserActionView(AdminRequiredMixin, View):
    """API view for admin user management actions."""
    def post(self, request, *args, **kwargs):
        action = request.POST.get("action")
        user_id = request.POST.get("user_id")
        
        if action == "create_user":
            email = request.POST.get("email", "").strip()
            role = request.POST.get("role", "MEMBER")
            password = request.POST.get("password", "").strip()
            
            if not email or not password:
                return JsonResponse({"success": False, "error": "Email and password are required."}, status=400)
            if User.objects.filter(email=email).exists():
                return JsonResponse({"success": False, "error": "A user with this email already exists."}, status=400)
                
            user = User.objects.create_user(email=email, password=password, role=role, is_email_verified=True)
            return JsonResponse({"success": True, "message": f"User {user.email} created successfully."})

        target_user = get_object_or_404(User, pk=user_id)
        
        if action == "toggle_status":
            if target_user == request.user:
                return JsonResponse({"success": False, "error": "You cannot deactivate your own account."}, status=400)
            target_user.is_active = not target_user.is_active
            target_user.save()
            status_str = "activated" if target_user.is_active else "deactivated"
            return JsonResponse({"success": True, "message": f"User {target_user.email} has been {status_str}.", "is_active": target_user.is_active})
            
        elif action == "change_role":
            new_role = request.POST.get("role")
            if new_role not in ["ADMIN", "MANAGER", "MEMBER"]:
                return JsonResponse({"success": False, "error": "Invalid role specified."}, status=400)
            if target_user == request.user and new_role != "ADMIN":
                return JsonResponse({"success": False, "error": "You cannot demote yourself from Admin."}, status=400)
            target_user.role = new_role
            if new_role == "ADMIN":
                target_user.is_staff = True
            target_user.save()
            return JsonResponse({"success": True, "message": f"Role for {target_user.email} updated to {new_role}.", "role": new_role})
            
        elif action == "delete_user":
            if target_user == request.user:
                return JsonResponse({"success": False, "error": "You cannot delete your own account."}, status=400)
            email = target_user.email
            target_user.delete()
            return JsonResponse({"success": True, "message": f"User {email} deleted successfully."})

        return JsonResponse({"success": False, "error": "Invalid action."}, status=400)


class AdminMeetingActionView(AdminRequiredMixin, View):
    """API view for admin meeting actions."""
    def post(self, request, *args, **kwargs):
        action = request.POST.get("action")
        meeting_id = request.POST.get("meeting_id")
        meeting = get_object_or_404(Meeting, pk=meeting_id)
        
        if action == "end_meeting":
            meeting.status = "COMPLETED"
            meeting.save()
            return JsonResponse({"success": True, "message": f"Meeting '{meeting.title}' session ended.", "status": "COMPLETED"})
            
        elif action == "delete_meeting":
            title = meeting.title
            meeting.delete()
            return JsonResponse({"success": True, "message": f"Meeting '{title}' deleted successfully."})
            
        return JsonResponse({"success": False, "error": "Invalid action."}, status=400)


class AdminExportReportView(AdminRequiredMixin, View):
    """View for generating CSV exports for system reports."""
    def get(self, request, *args, **kwargs):
        report_type = request.GET.get("type", "users")
        
        if report_type == "users":
            response = HttpResponse(content_type="text/csv")
            response["Content-Disposition"] = 'attachment; filename="meetflow_users_report.csv"'
            writer = csv.writer(response)
            writer.writerow(["ID", "Email", "Role", "Is Active", "Email Verified", "Joined Date"])
            for u in User.objects.all().order_by('-created_at'):
                writer.writerow([u.id, u.email, u.role, u.is_active, u.is_email_verified, u.created_at.strftime("%Y-%m-%d %H:%M:%S")])
            return response
            
        elif report_type == "meetings":
            response = HttpResponse(content_type="text/csv")
            response["Content-Disposition"] = 'attachment; filename="meetflow_meetings_report.csv"'
            writer = csv.writer(response)
            writer.writerow(["ID", "Title", "Room Code", "Meeting ID", "Host", "Type", "Status", "Start Time", "Duration (mins)"])
            for m in Meeting.objects.select_related('host').all().order_by('-created_at'):
                writer.writerow([m.id, m.title, m.room_code, m.meeting_id, m.host.email, m.meeting_type, m.status, m.start_time.strftime("%Y-%m-%d %H:%M:%S"), m.duration or 0])
            return response

        return HttpResponse("Invalid report type.", status=400)


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
