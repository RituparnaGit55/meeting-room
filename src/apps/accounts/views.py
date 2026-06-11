from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login as django_login
from django.contrib.auth.decorators import login_required
from .models import User
from .serializers import (
    UserSerializer, RegisterSerializer, LoginSerializer, ChangePasswordSerializer,
    PasswordResetRequestSerializer, PasswordResetSerializer, GoogleOAuthSerializer
)
from .services.user_service import (
    UserService, EmailVerificationTokenService, PasswordResetTokenService, GoogleOAuthService
)
from .permissions import IsOwnerOrAdmin
from .forms import (
    UserRegistrationForm, UserLoginForm, UserProfileForm, 
    PasswordResetRequestForm, PasswordResetForm, ChangePasswordForm
)


# API Views
class RegisterView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        
        # Generate tokens
        from rest_framework_simplejwt.tokens import RefreshToken
        refresh = RefreshToken.for_user(user)
        
        return Response({
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user": UserSerializer(user).data,
        }, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        user = UserService.register_user(
            email=serializer.validated_data["email"],
            password=serializer.validated_data["password"],
            first_name=serializer.validated_data.get("first_name"),
            last_name=serializer.validated_data.get("last_name"),
            department=serializer.validated_data.get("department"),
            phone=serializer.validated_data.get("phone"),
        )
        return user


class LoginView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = LoginSerializer

    def post(self, request):
        try:
            result = UserService.login_user(
                request.data["email"],
                request.data["password"]
            )
            return Response({
                "access": result["access"],
                "refresh": result["refresh"],
                "user": UserSerializer(result["user"]).data,
            })
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class RefreshTokenView(generics.GenericAPIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            refresh = RefreshToken(request.data["refresh"])
            return Response({
                "access": str(refresh.access_token),
            })
        except Exception:
            return Response({"error": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            UserService.logout_user(request.data["refresh"])
            return Response({"message": "Logged out successfully"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user


class ChangePasswordView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ChangePasswordSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            UserService.change_password(
                request.user,
                serializer.validated_data["old_password"],
                serializer.validated_data["new_password"],
            )
            return Response({"message": "Password changed successfully"}, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class EmailVerificationView(generics.GenericAPIView):
    permission_classes = [AllowAny]

    def get(self, request, token):
        try:
            EmailVerificationTokenService.verify_token(token)
            return Response({"message": "Email verified successfully"}, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class ResendVerificationEmailView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        EmailVerificationTokenService.create_and_send_token(request.user)
        return Response({"message": "Verification email sent"}, status=status.HTTP_200_OK)


class PasswordResetRequestView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = PasswordResetRequestSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        PasswordResetTokenService.create_and_send_token(serializer.validated_data["email"])
        return Response({"message": "Password reset email sent if email exists"}, status=status.HTTP_200_OK)


class PasswordResetView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = PasswordResetSerializer

    def post(self, request, token):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            PasswordResetTokenService.reset_password(
                token,
                serializer.validated_data["new_password"],
            )
            return Response({"message": "Password reset successfully"}, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class GoogleOAuthView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = GoogleOAuthSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            user_info = GoogleOAuthService.get_google_user_info(serializer.validated_data["access_token"])
            result = GoogleOAuthService.login_or_register(user_info)
            return Response({
                "access": result["access"],
                "refresh": result["refresh"],
                "user": UserSerializer(result["user"]).data,
            })
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


# Web Views (for frontend)
def register_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            try:
                UserService.register_user(
                    email=form.cleaned_data["email"],
                    password=form.cleaned_data["password"],
                    first_name=form.cleaned_data["first_name"],
                    last_name=form.cleaned_data["last_name"],
                    department=form.cleaned_data.get("department"),
                    phone=form.cleaned_data.get("phone"),
                )
                messages.success(request, "Registration successful! You can now login.")
                return redirect("login")
            except Exception as e:
                messages.error(request, str(e))
    else:
        form = UserRegistrationForm()
    return render(request, "accounts/register.html", {"form": form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    
    if request.method == "POST":
        form = UserLoginForm(request.POST)
        if form.is_valid():
            try:
                user = form.cleaned_data["user"]
                result = UserService.login_user(user.email, request.POST["password"])
                django_login(request, user)
                request.session["access_token"] = result["access"]
                request.session["refresh_token"] = result["refresh"]
                return redirect("dashboard")
            except ValueError as e:
                messages.error(request, str(e))
    else:
        form = UserLoginForm()
    return render(request, "accounts/login.html", {"form": form})


def logout_view(request):
    request.session.flush()
    return redirect("login")


def verify_email_view(request, token):
    try:
        EmailVerificationTokenService.verify_token(token)
        messages.success(request, "Email verified successfully! You can now login.")
        return redirect("login")
    except ValueError as e:
        messages.error(request, str(e))
        return redirect("login")


def forgot_password_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    
    if request.method == "POST":
        form = PasswordResetRequestForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            new_password = form.cleaned_data["new_password"]
            try:
                user = User.objects.get(email=email)
                user.set_password(new_password)
                user.save()
                messages.success(request, "Your password has been reset successfully! You can now login.")
                return redirect("login")
            except Exception as e:
                messages.error(request, f"An error occurred: {str(e)}")
    else:
        form = PasswordResetRequestForm()
    return render(request, "accounts/forgot_password.html", {"form": form})


def forgot_password_done_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    email = request.session.get("password_reset_email", "")
    return render(request, "accounts/password_reset_sent.html", {"email": email})


def reset_password_view(request, token):
    if request.user.is_authenticated:
        return redirect("dashboard")
    
    token_obj = PasswordResetTokenService.get_token(token)
    if not token_obj or token_obj.is_expired():
        messages.error(request, "Invalid or expired password reset token.")
        return redirect("forgot_password")
    
    if request.method == "POST":
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            try:
                PasswordResetTokenService.reset_password(token, form.cleaned_data["new_password"])
                return redirect("reset-password-success")
            except ValueError as e:
                messages.error(request, str(e))
    else:
        form = PasswordResetForm()
    return render(request, "accounts/reset_password.html", {"form": form, "token": token})


def reset_password_success_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    return render(request, "accounts/password_reset_success.html")


@login_required
def profile_view(request):
    if request.method == "POST":
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect("profile")
    else:
        form = UserProfileForm(instance=request.user)
    return render(request, "accounts/profile.html", {"form": form, "user": request.user})


@login_required
def change_password_view(request):
    if request.method == "POST":
        form = ChangePasswordForm(request.POST, user=request.user)
        if form.is_valid():
            UserService.change_password(
                request.user,
                form.cleaned_data["old_password"],
                form.cleaned_data["new_password"],
            )
            messages.success(request, "Password changed successfully!")
            return redirect("profile")
    else:
        form = ChangePasswordForm(user=request.user)
    return render(request, "accounts/change_password.html", {"form": form})
