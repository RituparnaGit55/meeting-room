
from django import forms
from django.contrib.auth import authenticate
from .models import User


class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter password'
    }))
    password_confirm = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Confirm password'
    }))

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'phone']
        widgets = {
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter email'
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter first name'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter last name'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter phone number'
            }),
        }

    def clean_email(self):
        email = (self.cleaned_data.get('email') or '').strip().lower()
        if email:
            if User.objects.filter(email__iexact=email).exists():
                raise forms.ValidationError("User with this Email already exists.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data is None:
            cleaned_data = {}
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')
        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError("Passwords don't match")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = (user.email or '').strip().lower()
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user


class UserLoginForm(forms.Form):
    email = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter User ID or email'
    }), label="User ID / Email")
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter password'
    }))

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data is None:
            cleaned_data = {}
        email = (cleaned_data.get('email') or '').strip().lower()
        password = cleaned_data.get('password')
        if email and password:
            user = authenticate(username=email, password=password)
            if not user:
                try:
                    candidate = User.objects.get(email__iexact=email)
                    if candidate.check_password(password):
                        user = candidate
                except User.DoesNotExist:
                    user = None
            if not user:
                raise forms.ValidationError("Invalid User ID or password")
            if not user.is_active:
                raise forms.ValidationError("This account is inactive")
            cleaned_data['user'] = user
        return cleaned_data


class AdminLoginForm(forms.Form):
    email = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter User ID or email'
    }), label="User ID / Email")
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter password'
    }))

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data is None:
            cleaned_data = {}
        email = (cleaned_data.get('email') or '').strip().lower()
        password = cleaned_data.get('password')
        if email and password:
            user = authenticate(username=email, password=password)
            if not user:
                try:
                    candidate = User.objects.get(email__iexact=email)
                    if candidate.check_password(password):
                        user = candidate
                except User.DoesNotExist:
                    user = None
            if not user:
                raise forms.ValidationError("Invalid User ID or password")
            if not user.is_active:
                raise forms.ValidationError("This account is inactive")
            if not (getattr(user, 'role', None) == 'ADMIN' or getattr(user, 'is_superuser', False) or getattr(user, 'is_staff', False)):
                raise forms.ValidationError("Access denied. Only administrators and staff members are allowed to log in here.")
            cleaned_data['user'] = user
        return cleaned_data


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'department', 'phone', 'bio', 'avatar']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control form-control-modern', 'placeholder': 'Enter first name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control form-control-modern', 'placeholder': 'Enter last name'}),
            'department': forms.TextInput(attrs={'class': 'form-control form-control-modern', 'placeholder': 'e.g. Engineering, Product'}),
            'phone': forms.TextInput(attrs={'class': 'form-control form-control-modern', 'placeholder': '+1 (555) 000-0000'}),
            'bio': forms.Textarea(attrs={'class': 'form-control form-control-modern', 'rows': 3, 'placeholder': 'Write a short bio about yourself...'}),
            'avatar': forms.ClearableFileInput(attrs={'class': 'form-control form-control-modern d-none', 'id': 'avatarFileInput', 'accept': 'image/*'}),
        }


class PasswordResetRequestForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter your email',
        'autocomplete': 'email'
    }))
    new_password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter new password',
        'autocomplete': 'new-password'
    }))
    new_password_confirm = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Re-enter new password',
        'autocomplete': 'new-password'
    }))

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and not User.objects.filter(email=email).exists():
            raise forms.ValidationError("No registered user found with this email address.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data is None:
            cleaned_data = {}
        new_password = cleaned_data.get('new_password')
        new_password_confirm = cleaned_data.get('new_password_confirm')
        if new_password and new_password_confirm and new_password != new_password_confirm:
            raise forms.ValidationError("Passwords don't match")
        return cleaned_data



class PasswordResetForm(forms.Form):
    new_password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter new password',
        'autocomplete': 'new-password'
    }))
    new_password_confirm = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Re-enter new password',
        'autocomplete': 'new-password'
    }))

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data is None:
            cleaned_data = {}
        new_password = cleaned_data.get('new_password')
        new_password_confirm = cleaned_data.get('new_password_confirm')
        if new_password and new_password_confirm and new_password != new_password_confirm:
            raise forms.ValidationError("Passwords don't match")
        return cleaned_data


class ChangePasswordForm(forms.Form):
    old_password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter current password',
        'autocomplete': 'current-password'
    }))
    new_password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter new password',
        'autocomplete': 'new-password'
    }))
    new_password_confirm = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Re-enter new password',
        'autocomplete': 'new-password'
    }))

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def clean_old_password(self):
        old_password = self.cleaned_data.get('old_password')
        if self.user and not self.user.check_password(old_password):
            raise forms.ValidationError("Current password is incorrect")
        return old_password

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data is None:
            cleaned_data = {}
        new_password = cleaned_data.get('new_password')
        new_password_confirm = cleaned_data.get('new_password_confirm')
        if new_password and new_password_confirm and new_password != new_password_confirm:
            raise forms.ValidationError("Passwords don't match")
        return cleaned_data
