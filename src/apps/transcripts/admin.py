from django.contrib import admin
from .models import Transcript


@admin.register(Transcript)
class TranscriptAdmin(admin.ModelAdmin):
    list_display = ("meeting", "speaker", "created_at")
