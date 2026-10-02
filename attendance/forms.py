from django import forms
from django.utils import timezone

from courses.models import Lesson
from schedule.models import GroupLesson


class GroupLessonForm(forms.ModelForm):
    class Meta:
        model = GroupLesson
        fields = ['lesson', 'date', 'teacher']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
        }

    def __init__(self, *args, group=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.group = group
        self.fields['date'].initial = timezone.localdate()
        self.fields['teacher'].required = False
        if group is not None:
            self.fields['lesson'].queryset = Lesson.objects.filter(
                module__course=group.course
            ).select_related('module')
            self.fields['teacher'].initial = group.teacher_id

    def save(self, commit=True):
        obj = super().save(commit=False)
        if self.group is not None:
            obj.group = self.group
            if obj.teacher_id is None:
                obj.teacher = self.group.teacher
        if commit:
            obj.save()
        return obj


class AttendanceMarkForm(forms.Form):
    def __init__(self, *args, students=None, existing=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.students = list(students or [])
        existing = existing or {}
        for student in self.students:
            field_name = f'status_{student.pk}'
            self.fields[field_name] = forms.ChoiceField(
                choices=[
                    ('present', 'Keldi'),
                    ('late', 'Kechikdi'),
                    ('absent', 'Kelmadi'),
                ],
                widget=forms.RadioSelect,
                initial=existing.get(student.pk),
                required=True,
                label=str(student),
            )

    def cleaned_statuses(self):
        result = {}
        for student in self.students:
            result[student] = self.cleaned_data[f'status_{student.pk}']
        return result
