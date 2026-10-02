from django.contrib.auth.models import AbstractUser
from django.db import models


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class CustomUser(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = 'admin', 'Admin'
        TEACHER = 'teacher', 'Teacher'
        MENTOR = 'mentor', 'Mentor'
        STUDENT = 'student', 'Student'

    role = models.CharField(max_length=10, choices=Role.choices, default=Role.STUDENT)
    phone = models.CharField(max_length=20, blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True)

    def __str__(self):
        return self.get_full_name() or self.username


class TeacherProfile(TimeStampedModel):
    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='teacher_profile',
        limit_choices_to={'role': CustomUser.Role.TEACHER},
    )
    specialization = models.CharField(max_length=100, blank=True)
    bio = models.TextField(blank=True)

    def __str__(self):
        return str(self.user)


class StudentProfile(TimeStampedModel):
    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='student_profile',
        limit_choices_to={'role': CustomUser.Role.STUDENT},
    )
    birth_date = models.DateField(null=True, blank=True)
    parent_phone = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return str(self.user)

    @property
    def coin_balance(self):
        result = self.coin_transactions.aggregate(total=models.Sum('amount'))
        return result['total'] or 0