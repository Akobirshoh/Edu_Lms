from attendance.models import Attendance
from coins.models import CoinTransaction


ATTENDANCE_COINS = {
    Attendance.Status.PRESENT: 5,
    Attendance.Status.LATE: 2,
    Attendance.Status.ABSENT: 0,
}


def award_attendance_coins(attendance, created_by):
    amount = ATTENDANCE_COINS.get(attendance.status, 0)
    if amount <= 0:
        return None

    marker = f'attendance:{attendance.pk}'
    exists = CoinTransaction.objects.filter(
        student=attendance.student,
        reason=CoinTransaction.Reason.ATTENDANCE,
        comment__contains=marker,
    ).exists()
    if exists:
        return None

    lesson = attendance.group_lesson.lesson
    date = attendance.group_lesson.date
    comment = f'{marker} | {lesson.title} ({date})'
    return CoinTransaction.objects.create(
        student=attendance.student,
        amount=amount,
        reason=CoinTransaction.Reason.ATTENDANCE,
        comment=comment,
        created_by=created_by,
    )
