from django.contrib import admin
from .models import Webhook


@admin.register(Webhook)
class WebhookAdmin(admin.ModelAdmin):
    list_display = ("user", "event", "url", "is_active")
