from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import CustomUser, StudentProfile, TeacherProfile


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ("username", "email", "role", "phone", "is_active", "is_staff")
    list_filter = ("role", "is_active", "is_staff")
    search_fields = ("username", "first_name", "last_name", "phone")
    fieldsets = UserAdmin.fieldsets + (
        ("Qo‘shimcha", {"fields": ("role", "phone", "avatar")}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Qo‘shimcha", {"fields": ("role", "phone", "avatar")}),
    )


class TeacherProfileInline(admin.StackedInline):
    model = TeacherProfile
    can_delete = False


class StudentProfileInline(admin.StackedInline):
    model = StudentProfile
    can_delete = False


@admin.register(TeacherProfile)
class TeacherProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "specialization")
    search_fields = ("user__username", "user__first_name", "specialization")


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "birth_date", "parent_phone")
    search_fields = ("user__username", "user__first_name", "parent_phone")
