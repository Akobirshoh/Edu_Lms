from datetime import date

from django.contrib import messages
from django.db import transaction
from django.db.models import Count, Prefetch, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from accounts.decorators import staff_roles
from courses.forms.group import GroupForm, GroupStudentAddForm, GroupStudentRemoveForm
from courses.models import Group, GroupStudent


@staff_roles
@require_http_methods(["GET"])
def group_list(request):
    groups = (
        Group.objects.select_related("course", "teacher__user", "mentor")
        .annotate(
            students_count=Count(
                "memberships",
                filter=Q(memberships__is_active=True),
                distinct=True,
            )
        )
        .order_by("name")
    )
    return render(request, "group/list.html", {"groups": groups})


@staff_roles
@require_http_methods(["GET", "POST"])
def group_create(request):
    if request.method == "POST":
        form = GroupForm(request.POST)
        if form.is_valid():
            group = form.save()
            messages.success(request, "Guruh yaratildi.")
            return redirect("group_detail", pk=group.pk)
        messages.error(request, "Formada xatolik bor.")
    else:
        form = GroupForm()
    return render(request, "group/create.html", {"form": form, "group": None})


@staff_roles
@require_http_methods(["GET", "POST"])
def group_update(request, pk):
    group = get_object_or_404(
        Group.objects.select_related("course", "teacher__user", "mentor"),
        pk=pk,
    )
    if request.method == "POST":
        form = GroupForm(request.POST, instance=group)
        if form.is_valid():
            form.save()
            messages.success(request, "Guruh yangilandi.")
            return redirect("group_detail", pk=group.pk)
        messages.error(request, "Formada xatolik bor.")
    else:
        form = GroupForm(instance=group)
    return render(request, "group/create.html", {"form": form, "group": group})


@staff_roles
@require_http_methods(["GET"])
def group_detail(request, pk):
    group = get_object_or_404(
        Group.objects.select_related("course", "teacher__user", "mentor").prefetch_related(
            Prefetch(
                "memberships",
                queryset=GroupStudent.objects.filter(is_active=True)
                .select_related("student__user")
                .order_by("joined_at"),
                to_attr="active_memberships",
            ),
            "schedules__room",
        ),
        pk=pk,
    )
    add_form = GroupStudentAddForm(group=group)
    remove_form = GroupStudentRemoveForm(group=group)
    return render(
        request,
        "group/detail.html",
        {
            "group": group,
            "add_form": add_form,
            "remove_form": remove_form,
            "schedules": group.schedules.all(),
        },
    )


@staff_roles
@require_http_methods(["GET", "POST"])
def group_students_manage(request, group_id):
    group = get_object_or_404(
        Group.objects.select_related("course", "teacher__user"),
        pk=group_id,
    )
    add_form = GroupStudentAddForm(group=group)
    remove_form = GroupStudentRemoveForm(group=group)

    if request.method == "POST":
        if "add_submit" in request.POST:
            add_form = GroupStudentAddForm(request.POST, group=group)
            if add_form.is_valid():
                students = add_form.cleaned_data["students"]
                with transaction.atomic():
                    for student in students:
                        GroupStudent.objects.update_or_create(
                            group=group,
                            student=student,
                            defaults={
                                "is_active": True,
                                "joined_at": date.today(),
                                "left_at": None,
                            },
                        )
                messages.success(request, f"{students.count()} ta o‘quvchi qo‘shildi.")
                return redirect("group_students_manage", group_id=group.pk)
            messages.error(request, "Qo‘shish formasida xatolik.")
        elif "remove_submit" in request.POST:
            remove_form = GroupStudentRemoveForm(request.POST, group=group)
            if remove_form.is_valid():
                students = remove_form.cleaned_data["students"]
                with transaction.atomic():
                    GroupStudent.objects.filter(
                        group=group,
                        student__in=students,
                        is_active=True,
                    ).update(is_active=False, left_at=date.today())
                messages.success(request, f"{students.count()} ta o‘quvchi chiqarildi.")
                return redirect("group_students_manage", group_id=group.pk)
            messages.error(request, "Chiqarish formasida xatolik.")

    active_memberships = (
        GroupStudent.objects.filter(group=group, is_active=True)
        .select_related("student__user")
        .order_by("joined_at")
    )
    return render(
        request,
        "group/group_students_manage.html",
        {
            "group": group,
            "add_form": add_form,
            "remove_form": remove_form,
            "active_memberships": active_memberships,
        },
    )


list_group = group_list
create_group = group_create
