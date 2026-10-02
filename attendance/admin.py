from django.contrib import admin

from .models import Attendance


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ("student", "group_lesson", "status")
    list_filter = ("status", "group_lesson__group")
    search_fields = ("student__user__username", "student__user__first_name")
