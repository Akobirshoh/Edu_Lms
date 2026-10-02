from django.db import models

from accounts.models import StudentProfile, TimeStampedModel
from schedule.models import GroupLesson


class Attendance(TimeStampedModel):
    class Status(models.TextChoices):
        PRESENT = 'present', 'Keldi'
        LATE = 'late', 'Kechikdi'
        ABSENT = 'absent', 'Kelmadi'

    group_lesson = models.ForeignKey(GroupLesson, on_delete=models.CASCADE, related_name='attendances')
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='attendances')
    status = models.CharField(max_length=10, choices=Status.choices)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['group_lesson', 'student'], name='unique_attendance'),
        ]

    def __str__(self):
        return f'{self.student} — {self.group_lesson} — {self.get_status_display()}'
