from django.contrib import admin
from .models import Message


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("meeting", "user", "timestamp")
    list_filter = ("timestamp",)
