from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views.decorators.http import require_http_methods, require_POST

from accounts.decorators import admin_required
from accounts.forms.user import LoginForm, ProfileForm, RegisterForm
from accounts.models import CustomUser, StudentProfile, TeacherProfile
from accounts.views.student import student_dashboard_context
from coins.models import Purchase
from courses.models import Course, Group, Room
from news.models import News
from normativ.models import NormativAnswer
from schedule.models import GroupSchedule


def _redirect_by_role(user):
    return redirect("home")


def home(request):
    if not request.user.is_authenticated:
        weekday = timezone.localdate().isoweekday()
        news_list = News.objects.filter(is_published=True).select_related("author")[:5]
        courses = (
            Course.objects.filter(is_active=True)
            .annotate(
                modules_count=Count("modules", distinct=True),
                groups_count=Count("groups", distinct=True),
            )
            .order_by("title")[:12]
        )
        today_schedules = (
            GroupSchedule.objects.filter(weekday=weekday)
            .select_related("group", "room", "group__course")
            .order_by("start_time")
        )
        return render(
            request,
            "accounts/home.html",
            {
                "news_list": news_list,
                "courses": courses,
                "today_schedules": today_schedules,
            },
        )

    role = request.user.role
    if role == CustomUser.Role.ADMIN or role == CustomUser.Role.MENTOR or request.user.is_superuser:
        return _admin_mentor_dashboard(request)
    if role == CustomUser.Role.TEACHER:
        return _teacher_dashboard(request)
    if role == CustomUser.Role.STUDENT:
        return _student_dashboard(request)
    return redirect("login")


def _admin_mentor_dashboard(request):
    weekday = timezone.localdate().isoweekday()
    context = {
        "courses_count": Course.objects.filter(is_active=True).count(),
        "groups_count": Group.objects.filter(is_active=True).count(),
        "teachers_count": TeacherProfile.objects.count(),
        "students_count": StudentProfile.objects.filter(
            memberships__is_active=True,
        ).distinct().count(),
        "rooms_count": Room.objects.count(),
        "pending_purchases": Purchase.objects.filter(status=Purchase.Status.PENDING).count(),
        "unchecked_answers": NormativAnswer.objects.filter(score__isnull=True).count(),
        "today_schedules": list(
            GroupSchedule.objects.filter(weekday=weekday)
            .select_related("group", "room", "group__course", "group__teacher__user")
            .order_by("start_time")[:15]
        ),
        "recent_news": News.objects.filter(is_published=True).select_related("author")[:5],
    }
    return render(request, "accounts/dashboard_admin.html", context)


def _teacher_dashboard(request):
    profile = getattr(request.user, "teacher_profile", None)
    weekday = timezone.localdate().isoweekday()
    groups = []
    today_schedules = []
    unchecked_answers = 0
    if profile is not None:
        groups = list(
            Group.objects.filter(teacher=profile)
            .select_related("course")
            .annotate(
                students_count=Count(
                    "memberships",
                    filter=Q(memberships__is_active=True),
                    distinct=True,
                )
            )
            .order_by("name")
        )
        group_ids = [g.pk for g in groups]
        today_schedules = list(
            GroupSchedule.objects.filter(group_id__in=group_ids, weekday=weekday)
            .select_related("group", "room", "group__course")
            .order_by("start_time")
        )
        unchecked_answers = NormativAnswer.objects.filter(
            score__isnull=True,
            student__memberships__group__teacher=profile,
            student__memberships__is_active=True,
        ).distinct().count()
    pending_purchases = Purchase.objects.filter(status=Purchase.Status.PENDING).count()
    return render(
        request,
        "accounts/dashboard_teacher.html",
        {
            "teacher_profile": profile,
            "groups": groups,
            "today_schedules": today_schedules,
            "unchecked_answers": unchecked_answers,
            "pending_purchases": pending_purchases,
        },
    )


def _student_dashboard(request):
    context = student_dashboard_context(request.user)
    return render(request, "accounts/dashboard_student.html", context)


@require_http_methods(["GET", "POST"])
def login_view(request):
    if request.user.is_authenticated:
        return redirect("home")
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            user = form.cleaned_data["user"]
            login(request, user)
            messages.success(request, f"Xush kelibsiz, {user.get_full_name() or user.username}!")
            next_url = request.GET.get("next") or request.POST.get("next")
            if next_url:
                return redirect(next_url)
            return _redirect_by_role(user)
        messages.error(request, "Kirish amalga oshmadi.")
    else:
        form = LoginForm()
    return render(request, "accounts/login.html", {"form": form})


@require_http_methods(["GET", "POST"])
def logout_view(request):
    logout(request)
    messages.info(request, "Tizimdan chiqdingiz.")
    return redirect("login")


@login_required
def profile_view(request):
    user = request.user
    teacher_profile = getattr(user, "teacher_profile", None) if hasattr(user, "teacher_profile") else None
    student_profile = getattr(user, "student_profile", None) if hasattr(user, "student_profile") else None
    coin_balance = None
    if student_profile is not None:
        coin_balance = student_profile.coin_balance
    return render(
        request,
        "accounts/profile.html",
        {
            "profile_user": user,
            "teacher_profile": teacher_profile,
            "student_profile": student_profile,
            "coin_balance": coin_balance,
        },
    )


@login_required
@require_http_methods(["GET", "POST"])
def profile_edit(request):
    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profil yangilandi.")
            return redirect("profile")
        messages.error(request, "Formada xatolik bor.")
    else:
        form = ProfileForm(instance=request.user)
    return render(request, "accounts/profile_edit.html", {"form": form})


@admin_required
@require_http_methods(["GET", "POST"])
def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f"Foydalanuvchi yaratildi: {user.username}")
            return redirect("home")
        messages.error(request, "Ro‘yxatdan o‘tkazishda xatolik.")
    else:
        form = RegisterForm()
    return render(request, "accounts/register.html", {"form": form})
