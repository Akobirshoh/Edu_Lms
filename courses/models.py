from django.conf import settings
from django.db import models

from accounts.models import CustomUser, StudentProfile, TeacherProfile, TimeStampedModel


class Room(TimeStampedModel):
    name = models.CharField(max_length=100, unique=True)
    capacity = models.PositiveSmallIntegerField()

    def __str__(self):
        return self.name


class Course(TimeStampedModel):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    duration_months = models.PositiveSmallIntegerField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title


class Module(TimeStampedModel):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='modules')
    title = models.CharField(max_length=200)
    order = models.PositiveSmallIntegerField()

    class Meta:
        ordering = ['order']
        constraints = [
            models.UniqueConstraint(fields=['course', 'order'], name='unique_module_order'),
        ]

    def __str__(self):
        return f'{self.course} / {self.title}'


class Lesson(TimeStampedModel):
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=200)
    content = models.TextField(blank=True)
    order = models.PositiveSmallIntegerField()

    class Meta:
        ordering = ['order']
        constraints = [
            models.UniqueConstraint(fields=['module', 'order'], name='unique_lesson_order'),
        ]

    def __str__(self):
        return f'{self.module} / {self.title}'


class Group(TimeStampedModel):
    course = models.ForeignKey(Course, on_delete=models.PROTECT, related_name='groups')
    teacher = models.ForeignKey(TeacherProfile, on_delete=models.PROTECT, related_name='groups')
    mentor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='mentored_groups',
        limit_choices_to={'role': CustomUser.Role.MENTOR},
    )
    name = models.CharField(max_length=100, unique=True)
    start_date = models.DateField()
    is_active = models.BooleanField(default=True)
    students = models.ManyToManyField(
        StudentProfile,
        through='GroupStudent',
        related_name='groups',
    )

    class Meta:
        verbose_name = 'guruh'
        verbose_name_plural = 'guruhlar'

    def __str__(self):
        return self.name

    @property
    def active_students(self):
        return StudentProfile.objects.filter(
            memberships__group=self,
            memberships__is_active=True,
        ).select_related('user')


class GroupStudent(TimeStampedModel):
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='memberships')
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='memberships')
    joined_at = models.DateField()
    left_at = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['group', 'student'], name='unique_group_student'),
        ]

    def __str__(self):
        return f'{self.student} in {self.group}'
