from django.db import models

from accounts.models import TeacherProfile, TimeStampedModel
from courses.models import Group, Lesson, Room


class GroupSchedule(TimeStampedModel):
    class Weekday(models.IntegerChoices):
        MONDAY = 1, 'Dushanba'
        TUESDAY = 2, 'Seshanba'
        WEDNESDAY = 3, 'Chorshanba'
        THURSDAY = 4, 'Payshanba'
        FRIDAY = 5, 'Juma'
        SATURDAY = 6, 'Shanba'
        SUNDAY = 7, 'Yakshanba'

    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='schedules')
    weekday = models.PositiveSmallIntegerField(choices=Weekday.choices)
    start_time = models.TimeField()
    end_time = models.TimeField()
    room = models.ForeignKey(Room, on_delete=models.PROTECT, related_name='schedules')

    class Meta:
        ordering = ['weekday', 'start_time']

    def __str__(self):
        return f'{self.group} — {self.get_weekday_display()} {self.start_time:%H:%M}'


class GroupLesson(TimeStampedModel):
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='conducted_lessons')
    lesson = models.ForeignKey(Lesson, on_delete=models.PROTECT, related_name='conducted_lessons')
    date = models.DateField()
    teacher = models.ForeignKey(
        TeacherProfile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='conducted_lessons',
    )

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f'{self.group} — {self.lesson.title} ({self.date})'
