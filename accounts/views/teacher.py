from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from accounts.decorators import role_required, staff_roles
from accounts.forms.teacher import TeacherEditForm
from accounts.models import CustomUser, TeacherProfile
from courses.models import Group


@staff_roles
def teacher_list(request):
    teachers = (
        TeacherProfile.objects.select_related("user")
        .annotate(
            groups_count=Count("groups", filter=Q(groups__is_active=True), distinct=True),
            students_count=Count(
                "groups__memberships",
                filter=Q(groups__memberships__is_active=True),
                distinct=True,
            ),
        )
        .order_by("user__last_name", "user__first_name", "user__username")
    )
    return render(request, "accounts/teacher/list.html", {"teachers": teachers})


@role_required(CustomUser.Role.TEACHER, CustomUser.Role.ADMIN)
def teacher_profile(request, pk=None):
    if pk is not None:
        teacher = get_object_or_404(
            TeacherProfile.objects.select_related("user"),
            pk=pk,
        )
    else:
        teacher = get_object_or_404(
            TeacherProfile.objects.select_related("user"),
            user=request.user,
        )
    groups = (
        Group.objects.filter(teacher=teacher)
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
    return render(
        request,
        "accounts/teacher/teacher_profile.html",
        {"teacher": teacher, "groups": groups},
    )


@role_required(CustomUser.Role.TEACHER)
@require_http_methods(["GET", "POST"])
def teacher_edit(request):
    profile = get_object_or_404(
        TeacherProfile.objects.select_related("user"),
        user=request.user,
    )
    user = profile.user
    if request.method == "POST":
        form = TeacherEditForm(request.POST, user=user)
        if form.is_valid():
            form.save(profile=profile)
            if form.cleaned_data.get("password"):
                update_session_auth_hash(request, user)
            messages.success(request, "O‘qituvchi profili yangilandi.")
            return redirect("teacher_profile")
        messages.error(request, "Formada xatolik bor.")
    else:
        form = TeacherEditForm(
            user=user,
            initial={
                "username": user.username,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "phone": user.phone,
                "specialization": profile.specialization,
                "bio": profile.bio,
            },
        )
    return render(request, "accounts/teacher/edit_teacher.html", {"form": form, "teacher": profile})


@role_required(CustomUser.Role.TEACHER)
def my_groups(request):
    teacher = get_object_or_404(
        TeacherProfile.objects.select_related("user"),
        user=request.user,
    )
    groups = (
        Group.objects.filter(teacher=teacher)
        .select_related("course", "mentor")
        .annotate(
            students_count=Count(
                "memberships",
                filter=Q(memberships__is_active=True),
                distinct=True,
            )
        )
        .prefetch_related("memberships__student__user")
        .order_by("name")
    )
    return render(
        request,
        "accounts/teacher/teacher_group.html",
        {"groups": groups, "teacher": teacher},
    )
