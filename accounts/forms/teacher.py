from django import forms
from django.contrib.auth import get_user_model
from django.db import transaction

User = get_user_model()


class TeacherEditForm(forms.Form):
    username = forms.CharField(max_length=150, label="Login")
    first_name = forms.CharField(max_length=150, required=False, label="Ism")
    last_name = forms.CharField(max_length=150, required=False, label="Familiya")
    phone = forms.CharField(max_length=20, required=False, label="Telefon")
    specialization = forms.CharField(max_length=100, required=False, label="Mutaxassislik")
    bio = forms.CharField(widget=forms.Textarea, required=False, label="Bio")
    password = forms.CharField(
        widget=forms.PasswordInput,
        required=False,
        label="Yangi parol",
        help_text="O‘zgartirmasangiz bo‘sh qoldiring",
    )

    def __init__(self, *args, user=None, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_username(self):
        username = self.cleaned_data["username"]
        qs = User.objects.filter(username=username)
        if self.user is not None:
            qs = qs.exclude(pk=self.user.pk)
        if qs.exists():
            raise forms.ValidationError("Bu login band.")
        return username

    @transaction.atomic
    def save(self, profile):
        user = profile.user
        user.username = self.cleaned_data["username"]
        user.first_name = self.cleaned_data.get("first_name", "")
        user.last_name = self.cleaned_data.get("last_name", "")
        user.phone = self.cleaned_data.get("phone", "")
        if self.cleaned_data.get("password"):
            user.set_password(self.cleaned_data["password"])
        user.save()
        profile.specialization = self.cleaned_data.get("specialization", "")
        profile.bio = self.cleaned_data.get("bio", "")
        profile.save()
        return profile
