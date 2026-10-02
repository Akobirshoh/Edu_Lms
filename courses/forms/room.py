from django import forms

from courses.models import Room


class RoomForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = ["name", "capacity"]
        labels = {
            "name": "Xona nomi",
            "capacity": "Sig‘imi",
        }

    def clean_name(self):
        name = self.cleaned_data["name"].strip()
        qs = Room.objects.filter(name__iexact=name)
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("Bu nomli xona allaqachon mavjud.")
        return name

    def clean_capacity(self):
        capacity = self.cleaned_data["capacity"]
        if capacity < 1:
            raise forms.ValidationError("Sig‘im kamida 1 bo‘lishi kerak.")
        return capacity
