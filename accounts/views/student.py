from django.db.models import Count, Q, Sum

from accounts.models import StudentProfile
from attendance.models import Attendance
from courses.models import Group
from normativ.models import NormativAnswer
from schedule.models import GroupSchedule


def get_student_profile(user):
    if not hasattr(user, "student_profile"):
        return None
    return user.student_profile


def student_dashboard_context(user):
    profile = get_student_profile(user)
    context = {
        "student_profile": profile,
        "coin_balance": 0,
        "groups": [],
        "today_schedules": [],
        "recent_answers": [],
        "attendance_percent": None,
        "leaderboard_rank": None,
        "leaderboard_total": 0,
    }
    if profile is None:
        return context

    context["coin_balance"] = profile.coin_balance

    groups = (
        Group.objects.filter(
            memberships__student=profile,
            memberships__is_active=True,
        )
        .select_related("course", "teacher__user")
        .distinct()
    )
    context["groups"] = list(groups)

    group_ids = [g.pk for g in context["groups"]]
    from django.utils import timezone

    weekday = timezone.localdate().isoweekday()
    context["today_schedules"] = list(
        GroupSchedule.objects.filter(
            group_id__in=group_ids,
            weekday=weekday,
        )
        .select_related("group", "room", "group__course")
        .order_by("start_time")
    )

    context["recent_answers"] = list(
        NormativAnswer.objects.filter(student=profile)
        .select_related("question__normativ__lesson")
        .order_by("-created_at")[:5]
    )

    stats = Attendance.objects.filter(student=profile).aggregate(
        total=Count("id"),
        came=Count("id", filter=Q(status__in=[Attendance.Status.PRESENT, Attendance.Status.LATE])),
    )
    total = stats["total"] or 0
    if total:
        context["attendance_percent"] = round(100 * (stats["came"] or 0) / total, 1)
    else:
        context["attendance_percent"] = None

    balances = list(
        StudentProfile.objects.annotate(
            balance=Sum("coin_transactions__amount"),
        )
        .order_by("-balance", "user__last_name", "user__first_name")
        .values_list("pk", "balance")
    )
    context["leaderboard_total"] = len(balances)
    for idx, (pk, _balance) in enumerate(balances, start=1):
        if pk == profile.pk:
            context["leaderboard_rank"] = idx
            break

    return context
