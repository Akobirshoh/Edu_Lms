from django import forms

from schedule.models import GroupSchedule


class GroupScheduleForm(forms.ModelForm):
    class Meta:
        model = GroupSchedule
        fields = ['weekday', 'start_time', 'end_time', 'room']
        widgets = {
            'start_time': forms.TimeInput(attrs={'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'type': 'time'}),
        }

    def __init__(self, *args, group=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.group = group

    def clean(self):
        cleaned = super().clean()
        start_time = cleaned.get('start_time')
        end_time = cleaned.get('end_time')
        room = cleaned.get('room')
        weekday = cleaned.get('weekday')

        if start_time and end_time and end_time <= start_time:
            self.add_error('end_time', "Tugash vaqti boshlanishdan keyin bo'lishi kerak.")
            self.add_error('start_time', "Boshlanish vaqti tugashdan oldin bo'lishi kerak.")

        if not (start_time and end_time and room and weekday is not None):
            return cleaned

        qs = GroupSchedule.objects.filter(
            room=room,
            weekday=weekday,
            start_time__lt=end_time,
            end_time__gt=start_time,
        )
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        conflict = qs.select_related('group').first()
        if conflict:
            raise forms.ValidationError(
                f"Bu xona band: {conflict.group} "
                f"({conflict.start_time:%H:%M}-{conflict.end_time:%H:%M})"
            )

        if self.group is not None:
            group_qs = GroupSchedule.objects.filter(
                group=self.group,
                weekday=weekday,
                start_time__lt=end_time,
                end_time__gt=start_time,
            )
            if self.instance and self.instance.pk:
                group_qs = group_qs.exclude(pk=self.instance.pk)
            group_conflict = group_qs.select_related('room').first()
            if group_conflict:
                raise forms.ValidationError(
                    f"Guruh shu vaqtda band: {group_conflict.room} "
                    f"({group_conflict.start_time:%H:%M}-{group_conflict.end_time:%H:%M})"
                )

        return cleaned

    def save(self, commit=True):
        obj = super().save(commit=False)
        if self.group is not None:
            obj.group = self.group
        if commit:
            obj.save()
        return obj
