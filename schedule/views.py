from collections import defaultdict

from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from accounts.decorators import role_required, staff_roles
from accounts.models import CustomUser
from courses.models import Group
from schedule.forms import GroupScheduleForm
from schedule.models import GroupSchedule


def _can_manage_group(user, group):
    if user.is_superuser or user.role == CustomUser.Role.ADMIN:
        return True
    if user.role == CustomUser.Role.TEACHER and hasattr(user, 'teacher_profile'):
        return group.teacher_id == user.teacher_profile.id
    if user.role == CustomUser.Role.MENTOR:
        return group.mentor_id == user.id
    return False


@staff_roles
def schedule_create(request, group_id):
    group = get_object_or_404(Group, pk=group_id)
    if not _can_manage_group(request.user, group):
        messages.error(request, "Bu guruh jadvaliga ruxsat yo'q.")
        return redirect('weekly_schedule')

    if request.method == 'POST':
        form = GroupScheduleForm(request.POST, group=group)
        if form.is_valid():
            form.save()
            messages.success(request, "Jadval qatori qo'shildi.")
            return redirect('schedule_create', group_id=group.pk)
    else:
        form = GroupScheduleForm(group=group)

    schedules = group.schedules.select_related('room').all()
    return render(request, 'schedule/schedule_form.html', {
        'form': form,
        'group': group,
        'schedules': schedules,
    })


@staff_roles
def schedule_update(request, group_id, pk):
    group = get_object_or_404(Group, pk=group_id)
    schedule = get_object_or_404(GroupSchedule, pk=pk, group=group)
    if not _can_manage_group(request.user, group):
        messages.error(request, "Bu guruh jadvaliga ruxsat yo'q.")
        return redirect('weekly_schedule')

    if request.method == 'POST':
        form = GroupScheduleForm(request.POST, instance=schedule, group=group)
        if form.is_valid():
            form.save()
            messages.success(request, "Jadval yangilandi.")
            return redirect('schedule_create', group_id=group.pk)
    else:
        form = GroupScheduleForm(instance=schedule, group=group)

    return render(request, 'schedule/schedule_form.html', {
        'form': form,
        'group': group,
        'schedule': schedule,
    })


@staff_roles
def schedule_delete(request, group_id, pk):
    group = get_object_or_404(Group, pk=group_id)
    schedule = get_object_or_404(GroupSchedule, pk=pk, group=group)
    if not _can_manage_group(request.user, group):
        messages.error(request, "Bu guruh jadvaliga ruxsat yo'q.")
        return redirect('weekly_schedule')

    if request.method != 'POST':
        return render(request, 'schedule/schedule_confirm_delete.html', {
            'group': group,
            'schedule': schedule,
        })

    schedule.delete()
    messages.success(request, "Jadval qatori o'chirildi.")
    return redirect('schedule_create', group_id=group.pk)


@role_required(
    CustomUser.Role.ADMIN,
    CustomUser.Role.TEACHER,
    CustomUser.Role.MENTOR,
    CustomUser.Role.STUDENT,
)
def weekly_schedule(request):
    qs = GroupSchedule.objects.select_related('group', 'room', 'group__course').order_by(
        'weekday', 'start_time'
    )

    if request.user.role == CustomUser.Role.TEACHER and hasattr(request.user, 'teacher_profile'):
        qs = qs.filter(group__teacher=request.user.teacher_profile)
    elif request.user.role == CustomUser.Role.MENTOR:
        qs = qs.filter(group__mentor=request.user)
    elif request.user.role == CustomUser.Role.STUDENT and hasattr(request.user, 'student_profile'):
        qs = qs.filter(
            group__memberships__student=request.user.student_profile,
            group__memberships__is_active=True,
        )

    by_weekday = defaultdict(list)
    for item in qs:
        by_weekday[item.weekday].append(item)

    days = []
    for value, label in GroupSchedule.Weekday.choices:
        days.append({
            'weekday': value,
            'label': label,
            'items': by_weekday.get(value, []),
        })

    return render(request, 'schedule/weekly.html', {'days': days})
