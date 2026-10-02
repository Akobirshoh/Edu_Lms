import os
from datetime import date, time

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django

django.setup()

from accounts.models import CustomUser, StudentProfile, TeacherProfile
from coins.models import CoinTransaction, ShopItem
from courses.models import Course, Group, GroupStudent, Lesson, Module, Room
from news.models import News
from normativ.models import Normativ, NormativQuestion
from schedule.models import GroupSchedule

User = CustomUser

if not User.objects.filter(username="admin").exists():
    admin = User.objects.create_superuser(
        username="admin",
        email="admin@lms.uz",
        password="admin123",
        first_name="Admin",
        last_name="LMS",
        role=CustomUser.Role.ADMIN,
    )
else:
    admin = User.objects.get(username="admin")

if not User.objects.filter(username="teacher").exists():
    t_user = User.objects.create_user(
        username="teacher",
        password="teacher123",
        first_name="Aziz",
        last_name="Karimov",
        role=CustomUser.Role.TEACHER,
        phone="+998901112233",
    )
    teacher = TeacherProfile.objects.create(
        user=t_user, specialization="Python", bio="Python o‘qituvchisi"
    )
else:
    teacher = TeacherProfile.objects.get(user__username="teacher")

if not User.objects.filter(username="student").exists():
    s_user = User.objects.create_user(
        username="student",
        password="student123",
        first_name="Vali",
        last_name="Toshev",
        role=CustomUser.Role.STUDENT,
        phone="+998909998877",
    )
    student = StudentProfile.objects.create(user=s_user, parent_phone="+998901234567")
else:
    student = StudentProfile.objects.get(user__username="student")

if not User.objects.filter(username="student2").exists():
    s2 = User.objects.create_user(
        username="student2",
        password="student123",
        first_name="Malika",
        last_name="Yusupova",
        role=CustomUser.Role.STUDENT,
    )
    student2 = StudentProfile.objects.create(user=s2)
else:
    student2 = StudentProfile.objects.get(user__username="student2")

room1, _ = Room.objects.get_or_create(name="1-xona", defaults={"capacity": 16})
Course.objects.get_or_create(
    title="Python asoslari",
    defaults={
        "description": "Python dasturlash tilining asosiy tushunchalari.",
        "duration_months": 6,
        "is_active": True,
    },
)
course = Course.objects.get(title="Python asoslari")
mod, _ = Module.objects.get_or_create(course=course, order=1, defaults={"title": "Kirish"})
lesson1, _ = Lesson.objects.get_or_create(
    module=mod, order=1, defaults={"title": "O‘zgaruvchilar", "content": "O‘zgaruvchilar haqida"}
)
group, _ = Group.objects.get_or_create(
    name="P-01",
    defaults={"course": course, "teacher": teacher, "start_date": date(2026, 3, 1), "is_active": True},
)
for st in (student, student2):
    GroupStudent.objects.update_or_create(
        group=group,
        student=st,
        defaults={"joined_at": date(2026, 3, 1), "left_at": None, "is_active": True},
    )
GroupSchedule.objects.get_or_create(
    group=group,
    weekday=1,
    start_time=time(14, 0),
    defaults={"end_time": time(16, 0), "room": room1},
)
norm, _ = Normativ.objects.get_or_create(
    lesson=lesson1,
    title="O‘zgaruvchilar normativi",
    defaults={"description": "Asosiy savollar"},
)
NormativQuestion.objects.get_or_create(
    normativ=norm,
    order=1,
    defaults={"text": "O‘zgaruvchi nima va qanday e’lon qilinadi?", "max_score": 10},
)
ShopItem.objects.get_or_create(name="Daftar", defaults={"price": 8, "stock": 20, "is_active": True})
CoinTransaction.objects.get_or_create(
    student=student,
    amount=20,
    reason=CoinTransaction.Reason.MANUAL,
    defaults={"comment": "Boshlang‘ich bonus", "created_by": admin},
)
News.objects.get_or_create(
    title="Yangi semestr boshlandi",
    defaults={
        "body": "Python va Web kurslariga qabul ochildi.",
        "author": admin,
        "is_published": True,
    },
)
print("Seed OK: admin/admin123, teacher/teacher123, student/student123")
