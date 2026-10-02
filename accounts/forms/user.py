from django import forms
from django.contrib.auth import authenticate
from django.db import transaction

from accounts.models import CustomUser, StudentProfile, TeacherProfile


class LoginForm(forms.Form):
    username = forms.CharField(
        max_length=150,
        label="Login",
        widget=forms.TextInput(attrs={"placeholder": "Login", "autocomplete": "username"}),
    )
    password = forms.CharField(
        label="Parol",
        widget=forms.PasswordInput(attrs={"placeholder": "Parol", "autocomplete": "current-password"}),
    )

    def clean(self):
        cleaned = super().clean()
        username = cleaned.get("username")
        password = cleaned.get("password")
        if username and password:
            user = authenticate(username=username, password=password)
            if user is None:
                raise forms.ValidationError("Login yoki parol noto‘g‘ri.")
            if not user.is_active:
                raise forms.ValidationError("Bu akkaunt faol emas.")
            cleaned["user"] = user
        return cleaned


class ProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ["first_name", "last_name", "phone", "avatar"]
        labels = {
            "first_name": "Ism",
            "last_name": "Familiya",
            "phone": "Telefon",
            "avatar": "Avatar",
        }


class RegisterForm(forms.ModelForm):
    password = forms.CharField(
        label="Parol",
        widget=forms.PasswordInput,
        min_length=6,
    )
    password_confirm = forms.CharField(
        label="Parolni tasdiqlang",
        widget=forms.PasswordInput,
    )

    class Meta:
        model = CustomUser
        fields = [
            "username",
            "first_name",
            "last_name",
            "phone",
            "role",
            "password",
        ]
        labels = {
            "username": "Login",
            "first_name": "Ism",
            "last_name": "Familiya",
            "phone": "Telefon",
            "role": "Rol",
        }

    def clean_password_confirm(self):
        password = self.cleaned_data.get("password")
        confirm = self.cleaned_data.get("password_confirm")
        if password and confirm and password != confirm:
            raise forms.ValidationError("Parollar mos kelmadi.")
        return confirm

    def clean_role(self):
        role = self.cleaned_data["role"]
        if role not in CustomUser.Role.values:
            raise forms.ValidationError("Noto‘g‘ri rol.")
        return role

    @transaction.atomic
    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
            if user.role == CustomUser.Role.TEACHER:
                TeacherProfile.objects.get_or_create(user=user)
            elif user.role == CustomUser.Role.STUDENT:
                StudentProfile.objects.get_or_create(user=user)
        return user
