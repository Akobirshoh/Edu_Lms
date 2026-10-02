from django import template
from django.utils import timezone

from schedule.models import GroupSchedule

register = template.Library()


@register.simple_tag(takes_context=True)
def bugungi_darslar(context):
    request = context.get("request")
    weekday = timezone.localdate().isoweekday()
    qs = (
        GroupSchedule.objects.filter(weekday=weekday)
        .select_related("group", "room", "group__course", "group__teacher__user")
        .order_by("start_time")
    )
    if request is not None and getattr(request, "user", None) and request.user.is_authenticated:
        user = request.user
        if user.role == "teacher" and hasattr(user, "teacher_profile"):
            qs = qs.filter(group__teacher=user.teacher_profile)
        elif user.role == "student" and hasattr(user, "student_profile"):
            qs = qs.filter(
                group__memberships__student=user.student_profile,
                group__memberships__is_active=True,
            ).distinct()
        elif user.role == "mentor":
            qs = qs.filter(group__mentor=user)
    return list(qs)
