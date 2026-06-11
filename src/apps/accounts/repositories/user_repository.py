from typing import Optional
from django.contrib.auth import get_user_model
from ..models import User, EmailVerificationToken, PasswordResetToken

User = get_user_model()


class UserRepository:
    @staticmethod
    def create_user(email: str, password: str, **extra_fields) -> User:
        return User.objects.create_user(email=email, password=password, **extra_fields)

    @staticmethod
    def get_user_by_id(user_id: int) -> Optional[User]:
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None

    @staticmethod
    def get_user_by_email(email: str) -> Optional[User]:
        try:
            return User.objects.get(email=email)
        except User.DoesNotExist:
            return None

    @staticmethod
    def update_user(user: User, **kwargs) -> User:
        for key, value in kwargs.items():
            setattr(user, key, value)
        user.save()
        return user

    @staticmethod
    def delete_user(user: User) -> None:
        user.delete()


class EmailVerificationTokenRepository:
    @staticmethod
    def create_token(user: User) -> EmailVerificationToken:
        token, _ = EmailVerificationToken.objects.update_or_create(
            user=user, defaults={"expires_at": None}
        )
        return token

    @staticmethod
    def get_token(token: str) -> Optional[EmailVerificationToken]:
        try:
            return EmailVerificationToken.objects.get(token=token)
        except EmailVerificationToken.DoesNotExist:
            return None

    @staticmethod
    def delete_token(token: EmailVerificationToken) -> None:
        token.delete()


class PasswordResetTokenRepository:
    @staticmethod
    def create_token(user: User) -> PasswordResetToken:
        return PasswordResetToken.objects.create(user=user)

    @staticmethod
    def get_token(token: str) -> Optional[PasswordResetToken]:
        try:
            return PasswordResetToken.objects.get(token=token)
        except PasswordResetToken.DoesNotExist:
            return None

    @staticmethod
    def mark_token_as_used(token: PasswordResetToken) -> None:
        token.is_used = True
        token.save()
