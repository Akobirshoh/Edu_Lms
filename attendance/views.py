from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from accounts.decorators import staff_roles
from accounts.models import CustomUser
from attendance.forms import AttendanceMarkForm, GroupLessonForm
from attendance.models import Attendance
from attendance.services import award_attendance_coins
from courses.models import Group
from schedule.models import GroupLesson


def _can_manage_group(user, group):
    if user.is_superuser or user.role == CustomUser.Role.ADMIN:
        return True
    if user.role == CustomUser.Role.TEACHER and hasattr(user, 'teacher_profile'):
        return group.teacher_id == user.teacher_profile.id
    if user.role == CustomUser.Role.MENTOR:
        return group.mentor_id == user.id
    return False


@staff_roles
def create_group_lesson(request, group_id):
    group = get_object_or_404(Group, pk=group_id)
    if not _can_manage_group(request.user, group):
        messages.error(request, "Bu guruh darsiga ruxsat yo'q.")
        return redirect('group-list')

    if request.method == 'POST':
        form = GroupLessonForm(request.POST, group=group)
        if form.is_valid():
            group_lesson = form.save()
            messages.success(request, "Dars qayd qilindi.")
            return redirect('mark_attendance', group_lesson_id=group_lesson.pk)
    else:
        form = GroupLessonForm(group=group)

    return render(request, 'attendance/create_lesson.html', {
        'form': form,
        'group': group,
    })


@staff_roles
def mark_attendance(request, group_lesson_id):
    group_lesson = get_object_or_404(
        GroupLesson.objects.select_related('group', 'lesson', 'teacher'),
        pk=group_lesson_id,
    )
    group = group_lesson.group
    if not _can_manage_group(request.user, group):
        messages.error(request, "Bu davomatga ruxsat yo'q.")
        return redirect('group-list')

    students = list(group.active_students)
    existing = {
        a.student_id: a.status
        for a in Attendance.objects.filter(group_lesson=group_lesson)
    }

    if request.method == 'POST':
        form = AttendanceMarkForm(request.POST, students=students, existing=existing)
        if form.is_valid():
            for student, status in form.cleaned_statuses().items():
                attendance, created = Attendance.objects.update_or_create(
                    group_lesson=group_lesson,
                    student=student,
                    defaults={'status': status},
                )
                if created:
                    award_attendance_coins(attendance, request.user)
            messages.success(request, "Davomat saqlandi.")
            return redirect('mark_attendance', group_lesson_id=group_lesson.pk)
    else:
        form = AttendanceMarkForm(students=students, existing=existing)

    return render(request, 'attendance/mark.html', {
        'form': form,
        'group': group,
        'group_lesson': group_lesson,
        'students': students,
    })


@staff_roles
def group_journal(request, group_id):
    group = get_object_or_404(Group, pk=group_id)
    if not _can_manage_group(request.user, group):
        messages.error(request, "Bu jurnalga ruxsat yo'q.")
        return redirect('group-list')

    students = list(group.active_students)
    lessons = list(
        GroupLesson.objects.filter(group=group)
        .select_related('lesson')
        .order_by('date')
    )
    attendances = Attendance.objects.filter(group_lesson__group=group).select_related(
        'student', 'group_lesson'
    )
    matrix = {
        (a.student_id, a.group_lesson_id): a.status
        for a in attendances
    }

    return render(request, 'attendance/journal.html', {
        'group': group,
        'students': students,
        'lessons': lessons,
        'matrix': matrix,
    })
