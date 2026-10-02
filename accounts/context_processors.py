from django.utils import timezone

from schedule.models import GroupSchedule


def nav_context(request):
    today_lessons = []
    if request.user.is_authenticated:
        weekday = timezone.localdate().isoweekday()
        qs = GroupSchedule.objects.filter(weekday=weekday).select_related(
            "group", "room", "group__course"
        )
        if request.user.role == "teacher" and hasattr(request.user, "teacher_profile"):
            qs = qs.filter(group__teacher=request.user.teacher_profile)
        elif request.user.role == "student" and hasattr(request.user, "student_profile"):
            qs = qs.filter(
                group__memberships__student=request.user.student_profile,
                group__memberships__is_active=True,
            )
        today_lessons = list(qs.order_by("start_time")[:8])
    return {"today_lessons": today_lessons}
