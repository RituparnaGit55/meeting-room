from django.contrib import admin
from .models import Recording


@admin.register(Recording)
class RecordingAdmin(admin.ModelAdmin):
    list_display = ("meeting", "created_at", "is_uploaded_to_youtube")
