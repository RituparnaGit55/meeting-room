import urllib.request
from django.core.files.base import ContentFile
from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter


class CustomAccountAdapter(DefaultAccountAdapter):
    def get_login_redirect_url(self, request):
        """Redirect user to appropriate dashboard based on user role."""
        user = request.user
        if getattr(user, "role", None) == "ADMIN" or getattr(user, "is_superuser", False) or getattr(user, "is_staff", False):
            return "/admin-dashboard/"
        return "/meetings/my-meetings/"


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def get_app(self, request, provider, client_id=None):
        """Safely retrieve the SocialApp for a provider, avoiding MultipleObjectsReturned if defined in both settings and DB."""
        apps = self.list_apps(request, provider=provider, client_id=client_id)
        if apps:
            return apps[0]
        return super().get_app(request, provider, client_id=client_id)

    def populate_user(self, request, sociallogin, data):
        """Populate user instance from Google sociallogin data."""
        user = super().populate_user(request, sociallogin, data)
        extra_data = sociallogin.account.extra_data or {}
        
        # Ensure email is set
        if not user.email and "email" in extra_data:
            user.email = extra_data["email"]
            
        # Map first_name and last_name if available
        if "given_name" in extra_data and not user.first_name:
            user.first_name = extra_data["given_name"]
        if "family_name" in extra_data and not user.last_name:
            user.last_name = extra_data["family_name"]
        elif "name" in extra_data and not user.first_name:
            name_parts = extra_data["name"].split(" ", 1)
            user.first_name = name_parts[0]
            if len(name_parts) > 1 and not user.last_name:
                user.last_name = name_parts[1]
                
        # Mark email as verified for Google authenticated users
        user.is_email_verified = True
        
        # Set default role if not set
        if not getattr(user, "role", None):
            user.role = "MEMBER"
            
        return user

    def save_user(self, request, sociallogin, form=None):
        user = super().save_user(request, sociallogin, form=form)
        self._update_google_avatar(user, sociallogin)
        return user

    def pre_social_login(self, request, sociallogin):
        super().pre_social_login(request, sociallogin)
        if sociallogin.is_existing:
            self._update_google_avatar(sociallogin.user, sociallogin)

    def _update_google_avatar(self, user, sociallogin):
        """Fetch Google profile picture and save to user.avatar."""
        extra_data = sociallogin.account.extra_data or {}
        picture_url = extra_data.get("picture")
        if picture_url:
            try:
                # Upgrade picture resolution if s96-c
                if "=s96-c" in picture_url:
                    picture_url = picture_url.replace("=s96-c", "=s256-c")
                req = urllib.request.Request(picture_url, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req, timeout=10) as response:
                    img_data = response.read()
                    if img_data:
                        filename = f"google_avatar_{user.id}.jpg"
                        user.avatar.save(filename, ContentFile(img_data), save=True)
            except Exception as e:
                print("Failed to download Google avatar:", str(e))

    def get_login_redirect_url(self, request):
        """Redirect user to appropriate dashboard based on user role."""
        user = request.user
        if getattr(user, "role", None) == "ADMIN" or getattr(user, "is_superuser", False) or getattr(user, "is_staff", False):
            return "/admin-dashboard/"
        return "/meetings/my-meetings/"
