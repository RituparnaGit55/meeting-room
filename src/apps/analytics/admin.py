from django.contrib import admin
from .models import MeetingAnalytics, UserAnalytics


@admin.register(MeetingAnalytics)
class MeetingAnalyticsAdmin(admin.ModelAdmin):
    list_display = ("meeting", "total_participants", "created_at")


@admin.register(UserAnalytics)
class UserAnalyticsAdmin(admin.ModelAdmin):
    list_display = ("user", "total_meetings_hosted", "updated_at")
