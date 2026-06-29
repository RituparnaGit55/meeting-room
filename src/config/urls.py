from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect, render
from django.http import JsonResponse
from django.views.generic.base import RedirectView
from apps.notifications.views import NotificationPageView

def dashboard_view(request):
    """User dashboard — public landing page for unauthenticated users,
    role-based redirect for authenticated users."""
    if request.user.is_authenticated:
        # ADMIN users should use admin-dashboard
        if getattr(request.user, 'role', None) == 'ADMIN' or request.user.is_superuser:
            return redirect("admin-dashboard-page")
    return render(request, "meetings/dashboard.html")


def role_based_redirect(request):
    """Root URL redirect based on role."""
    if request.user.is_authenticated:
        if getattr(request.user, 'role', None) == 'ADMIN' or request.user.is_superuser:
            return redirect("admin-dashboard-page")
        return redirect("meeting-dashboard")
    return redirect("dashboard")


def test_auth_view(request):
    return JsonResponse({
        "authenticated": request.user.is_authenticated,
        "user": str(request.user) if request.user.is_authenticated else None
    })

urlpatterns = [
    path("favicon.ico", RedirectView.as_view(url=settings.STATIC_URL + "favicon.ico")),
    path("accounts/login/", RedirectView.as_view(pattern_name="login", query_string=True)),
    path("admin/", admin.site.urls),
    # Web URLs first
    path("auth/", include("apps.accounts.urls")),
    path("meetings/", include("apps.meetings.urls")),
    # API URLs (namespaced)
    path("api/v1/auth/", include(("apps.accounts.urls", "accounts-api"), namespace="accounts-api")),
    path("api/v1/meetings/", include(("apps.meetings.urls", "meetings-api"), namespace="meetings-api")),
    path("test-auth/", test_auth_view, name="test-auth"),
    # path("api/v1/participants/", include("apps.participants.urls")),
    path("api/v1/chat/", include("apps.chat.urls")),
    path("api/v1/recordings/", include("apps.recordings.urls")),
    path("api/v1/transcripts/", include("apps.transcripts.urls")),
    path("api/v1/summaries/", include("apps.summaries.urls")),
    path("api/v1/tasks/", include("apps.tasks.urls")),
    path("api/v1/notifications/", include("apps.notifications.urls")),
    path("api/v1/analytics/", include("apps.analytics.urls")),
    # path("api/v1/webhooks/", include("apps.webhooks.urls")),
    # path("api/v1/api_keys/", include("apps.api_keys.urls")),
    path("api/v1/dashboard/", include("apps.dashboard.urls")),
    path("notifications/", NotificationPageView.as_view(), name="notifications-page"),
    path("admin-dashboard/", include("apps.dashboard.urls")),
    path("", role_based_redirect),
    path("dashboard/", dashboard_view, name="dashboard"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    if "debug_toolbar" in settings.INSTALLED_APPS:
        try:
            debug_toolbar = __import__("debug_toolbar")
            urlpatterns = [path("__debug__/", include(debug_toolbar.urls))] + urlpatterns
        except ImportError:
            pass
