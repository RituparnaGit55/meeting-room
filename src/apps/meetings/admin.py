from django.contrib import admin
from .models import Meeting, MeetingParticipant, RestrictedKeyword


@admin.register(Meeting)
class MeetingAdmin(admin.ModelAdmin):
    list_display = ("title", "host", "meeting_type", "status", "start_time", "created_at")
    list_filter = ("status", "meeting_type", "created_at")
    search_fields = ("title", "host__email", "room_code", "meeting_id")
    readonly_fields = ("room_code", "meeting_id", "created_at", "updated_at")


@admin.register(MeetingParticipant)
class MeetingParticipantAdmin(admin.ModelAdmin):
    list_display = ("meeting", "user", "guest_name", "role", "status", "joined_at")
    list_filter = ("role", "status", "joined_at")
    search_fields = ("meeting__title", "user__email", "guest_name")


@admin.register(RestrictedKeyword)
class RestrictedKeywordAdmin(admin.ModelAdmin):
    list_display = ("meeting", "keyword", "status", "created_by", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("meeting__title", "meeting__room_code", "keyword")

