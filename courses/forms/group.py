from django import forms

from accounts.models import CustomUser, StudentProfile, TeacherProfile
from courses.models import Course, Group, GroupStudent


class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ["course", "teacher", "mentor", "name", "start_date", "is_active"]
        labels = {
            "course": "Kurs",
            "teacher": "O‘qituvchi",
            "mentor": "Mentor",
            "name": "Guruh nomi",
            "start_date": "Boshlanish sanasi",
            "is_active": "Faol",
        }
        widgets = {
            "start_date": forms.DateInput(
                attrs={"type": "date"},
                format="%Y-%m-%d",
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["course"].queryset = Course.objects.filter(is_active=True).order_by("title")
        self.fields["teacher"].queryset = TeacherProfile.objects.select_related("user").order_by(
            "user__last_name", "user__first_name"
        )
        self.fields["mentor"].queryset = CustomUser.objects.filter(
            role=CustomUser.Role.MENTOR,
            is_active=True,
        ).order_by("last_name", "first_name", "username")
        self.fields["mentor"].required = False
        self.fields["start_date"].input_formats = ["%Y-%m-%d"]

    def clean_name(self):
        name = self.cleaned_data["name"].strip()
        qs = Group.objects.filter(name__iexact=name)
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("Bu nomli guruh allaqachon mavjud.")
        return name


class GroupStudentAddForm(forms.Form):
    students = forms.ModelMultipleChoiceField(
        queryset=StudentProfile.objects.none(),
        widget=forms.CheckboxSelectMultiple,
        required=True,
        label="O‘quvchilar",
    )

    def __init__(self, *args, group=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.group = group
        already_in = GroupStudent.objects.filter(
            group=group,
            is_active=True,
        ).values_list("student_id", flat=True)
        self.fields["students"].queryset = (
            StudentProfile.objects.exclude(id__in=already_in)
            .select_related("user")
            .order_by("user__last_name", "user__first_name")
        )


class GroupStudentRemoveForm(forms.Form):
    students = forms.ModelMultipleChoiceField(
        queryset=StudentProfile.objects.none(),
        widget=forms.CheckboxSelectMultiple,
        required=True,
        label="O‘quvchilar",
    )

    def __init__(self, *args, group=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.group = group
        active_ids = GroupStudent.objects.filter(
            group=group,
            is_active=True,
        ).values_list("student_id", flat=True)
        self.fields["students"].queryset = (
            StudentProfile.objects.filter(id__in=active_ids)
            .select_related("user")
            .order_by("user__last_name", "user__first_name")
        )
