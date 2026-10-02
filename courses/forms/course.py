from django import forms

from courses.models import Course, Lesson, Module


class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ["title", "description", "duration_months", "is_active"]
        labels = {
            "title": "Nomi",
            "description": "Tavsif",
            "duration_months": "Davomiylik (oy)",
            "is_active": "Faol",
        }

    def clean_duration_months(self):
        value = self.cleaned_data["duration_months"]
        if not 1 <= value <= 24:
            raise forms.ValidationError("Davomiylik 1–24 oy oralig‘ida bo‘lishi kerak.")
        return value

    def clean_title(self):
        title = self.cleaned_data["title"].strip()
        qs = Course.objects.filter(title__iexact=title, is_active=True)
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("Shu nomli faol kurs allaqachon mavjud.")
        return title


class ModuleForm(forms.ModelForm):
    class Meta:
        model = Module
        fields = ["title", "order"]
        labels = {
            "title": "Modul nomi",
            "order": "Tartib",
        }

    def __init__(self, *args, course=None, **kwargs):
        self.course = course
        super().__init__(*args, **kwargs)
        if course is not None and not self.is_bound:
            last = course.modules.order_by("-order").first()
            self.fields["order"].initial = (last.order + 1) if last else 1

    def clean_order(self):
        order = self.cleaned_data["order"]
        if self.course is None:
            return order
        qs = Module.objects.filter(course=self.course, order=order)
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("Bu tartib raqami band.")
        return order

    def save(self, commit=True):
        module = super().save(commit=False)
        if self.course is not None:
            module.course = self.course
        if commit:
            module.save()
        return module


class LessonForm(forms.ModelForm):
    class Meta:
        model = Lesson
        fields = ["title", "content", "order"]
        labels = {
            "title": "Dars nomi",
            "content": "Mazmuni",
            "order": "Tartib",
        }

    def __init__(self, *args, module=None, **kwargs):
        self.module = module
        super().__init__(*args, **kwargs)
        if module is not None and not self.is_bound:
            last = module.lessons.order_by("-order").first()
            self.fields["order"].initial = (last.order + 1) if last else 1

    def clean_order(self):
        order = self.cleaned_data["order"]
        if self.module is None:
            return order
        qs = Lesson.objects.filter(module=self.module, order=order)
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("Bu tartib raqami band.")
        return order

    def save(self, commit=True):
        lesson = super().save(commit=False)
        if self.module is not None:
            lesson.module = self.module
        if commit:
            lesson.save()
        return lesson
