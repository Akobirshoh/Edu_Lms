from django.contrib import admin

from .models import Course, Group, GroupStudent, Lesson, Module, Room


class ModuleInline(admin.TabularInline):
    model = Module
    extra = 0


class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 0


class GroupStudentInline(admin.TabularInline):
    model = GroupStudent
    extra = 0


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ("name", "capacity")
    search_fields = ("name",)


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("title", "duration_months", "is_active")
    list_filter = ("is_active",)
    search_fields = ("title",)
    inlines = [ModuleInline]


@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ("title", "course", "order")
    list_filter = ("course",)
    inlines = [LessonInline]


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ("title", "module", "order")
    list_filter = ("module__course",)


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ("name", "course", "teacher", "start_date", "is_active")
    list_filter = ("is_active", "course")
    search_fields = ("name",)
    inlines = [GroupStudentInline]


@admin.register(GroupStudent)
class GroupStudentAdmin(admin.ModelAdmin):
    list_display = ("group", "student", "joined_at", "left_at", "is_active")
    list_filter = ("is_active", "group")
