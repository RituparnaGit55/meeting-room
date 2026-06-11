import requests
from django.conf import settings
from django.core.mail import send_mail
from django.contrib.auth import authenticate
from django.utils import timezone
from rest_framework_simplejwt.tokens import RefreshToken
from ..models import User
from ..repositories.user_repository import (
    UserRepository, EmailVerificationTokenRepository, PasswordResetTokenRepository
)


class UserService:
    @staticmethod
    def register_user(email: str, password: str, **extra_fields) -> User:
        # Check if user already exists
        existing_user = UserRepository.get_user_by_email(email)
        if existing_user:
            if not existing_user.is_email_verified:
                # Delete the old unverified user
                existing_user.delete()
            else:
                # User already exists and is verified
                raise ValueError("User with this Email already exists.")
        # Create new user and mark as verified immediately
        extra_fields["is_email_verified"] = True
        user = UserRepository.create_user(email, password, **extra_fields)
        # Email verification is disabled, don't send verification email
        # EmailVerificationTokenService.create_and_send_token(user)
        return user

    @staticmethod
    def login_user(email: str, password: str) -> dict:
        user = authenticate(email=email, password=password)
        if not user:
            raise ValueError("Invalid email or password")
        # Temporarily skip email verification for development
        # if not user.is_email_verified:
        #     raise ValueError("Email not verified")
        if not user.is_active:
            raise ValueError("Account deactivated")
        refresh = RefreshToken.for_user(user)
        return {
            "user": user,
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        }

    @staticmethod
    def logout_user(refresh_token: str) -> None:
        token = RefreshToken(refresh_token)
        token.blacklist()

    @staticmethod
    def get_user_profile(user: User) -> User:
        return user

    @staticmethod
    def update_user_profile(user: User, **kwargs) -> User:
        return UserRepository.update_user(user, **kwargs)

    @staticmethod
    def change_password(user: User, old_password: str, new_password: str) -> None:
        if not user.check_password(old_password):
            raise ValueError("Old password is incorrect")
        user.set_password(new_password)
        user.save()


class EmailVerificationTokenService:
    @staticmethod
    def create_and_send_token(user: User) -> None:
        token = EmailVerificationTokenRepository.create_token(user)
        verification_url = f"{settings.SITE_DOMAIN}/auth/verify-email/{token.token}/"
        send_mail(
            subject="Verify Your Email",
            message=f"Click the link to verify your email: {verification_url}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )

    @staticmethod
    def verify_token(token_str: str) -> User:
        token = EmailVerificationTokenRepository.get_token(token_str)
        if not token or token.is_expired():
            raise ValueError("Invalid or expired token")
        user = token.user
        user.is_email_verified = True
        user.save()
        token.delete()
        return user


class PasswordResetTokenService:
    @staticmethod
    def create_and_send_token(email: str) -> None:
        user = UserRepository.get_user_by_email(email)
        if user:
            token = PasswordResetTokenRepository.create_token(user)
            reset_url = f"{settings.SITE_DOMAIN}/auth/reset-password/{token.token}/"
            send_mail(
                subject="Password Reset Request",
                message=f"Click the link to reset your password: {reset_url}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False,
            )
    
    @staticmethod
    def get_token(token_str: str):
        return PasswordResetTokenRepository.get_token(token_str)

    @staticmethod
    def reset_password(token_str: str, new_password: str) -> None:
        token = PasswordResetTokenRepository.get_token(token_str)
        if not token or token.is_expired():
            raise ValueError("Invalid or expired token")
        user = token.user
        user.set_password(new_password)
        user.save()
        PasswordResetTokenRepository.mark_token_as_used(token)


class GoogleOAuthService:
    @staticmethod
    def get_google_user_info(access_token: str) -> dict:
        response = requests.get(
            "https://www.googleapis.com/oauth2/v2/userinfo",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        response.raise_for_status()
        return response.json()

    @staticmethod
    def get_or_create_user(user_info: dict) -> User:
        email = user_info.get("email")
        user = UserRepository.get_user_by_email(email)
        if user:
            return user
        return UserRepository.create_user(
            email=email,
            password=User.objects.make_random_password(),
            first_name=user_info.get("given_name", ""),
            last_name=user_info.get("family_name", ""),
            is_email_verified=True,
        )

    @staticmethod
    def login_or_register(user_info: dict) -> dict:
        user = GoogleOAuthService.get_or_create_user(user_info)
        refresh = RefreshToken.for_user(user)
        return {
            "user": user,
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        }
