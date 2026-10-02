from django.contrib import admin

from .models import GroupLesson, GroupSchedule


@admin.register(GroupSchedule)
class GroupScheduleAdmin(admin.ModelAdmin):
    list_display = ("group", "weekday", "start_time", "end_time", "room")
    list_filter = ("weekday", "room", "group")


@admin.register(GroupLesson)
class GroupLessonAdmin(admin.ModelAdmin):
    list_display = ("group", "lesson", "date", "teacher")
    list_filter = ("group", "date")
    date_hierarchy = "date"
