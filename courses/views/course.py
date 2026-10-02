from django.contrib import messages
from django.db.models import Count, Prefetch, ProtectedError
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from accounts.decorators import role_required
from accounts.models import CustomUser
from courses.forms.course import CourseForm, LessonForm, ModuleForm
from courses.models import Course, Lesson, Module


@require_http_methods(["GET"])
def course_list(request):
    courses = (
        Course.objects.filter(is_active=True)
        .annotate(
            modules_count=Count("modules", distinct=True),
            groups_count=Count("groups", distinct=True),
        )
        .order_by("title")
    )
    return render(
        request,
        "courses/course/list.html",
        {"courses": courses},
    )


@require_http_methods(["GET"])
def course_detail(request, pk):
    course = get_object_or_404(
        Course.objects.prefetch_related(
            Prefetch(
                "modules",
                queryset=Module.objects.prefetch_related(
                    Prefetch("lessons", queryset=Lesson.objects.order_by("order"))
                ).order_by("order"),
            ),
            "groups__teacher__user",
        ),
        pk=pk,
    )
    return render(request, "courses/course/detail.html", {"course": course})


@role_required(CustomUser.Role.ADMIN, CustomUser.Role.TEACHER)
@require_http_methods(["GET", "POST"])
def course_create(request):
    if request.method == "POST":
        form = CourseForm(request.POST)
        if form.is_valid():
            course = form.save()
            messages.success(request, "Kurs yaratildi.")
            return redirect("course_detail", pk=course.pk)
        messages.error(request, "Formada xatolik bor.")
    else:
        form = CourseForm()
    return render(request, "courses/course/create.html", {"form": form, "course": None})


@role_required(CustomUser.Role.ADMIN, CustomUser.Role.TEACHER)
@require_http_methods(["GET", "POST"])
def course_update(request, pk):
    course = get_object_or_404(Course, pk=pk)
    if request.method == "POST":
        form = CourseForm(request.POST, instance=course)
        if form.is_valid():
            form.save()
            messages.success(request, "Kurs yangilandi.")
            return redirect("course_detail", pk=course.pk)
        messages.error(request, "Formada xatolik bor.")
    else:
        form = CourseForm(instance=course)
    return render(request, "courses/course/create.html", {"form": form, "course": course})


@role_required(CustomUser.Role.ADMIN, CustomUser.Role.TEACHER)
@require_http_methods(["GET", "POST"])
def course_delete(request, pk):
    course = get_object_or_404(Course, pk=pk)
    if request.method == "POST":
        try:
            course.delete()
        except ProtectedError:
            messages.error(
                request,
                "Bu kursni o‘chirib bo‘lmaydi: unga bog‘langan guruhlar mavjud.",
            )
            return redirect("course_detail", pk=pk)
        messages.success(request, "Kurs o‘chirildi.")
        return redirect("course_list")
    return render(request, "courses/course/confirm_delete.html", {"course": course})


@role_required(CustomUser.Role.ADMIN, CustomUser.Role.TEACHER)
@require_http_methods(["GET", "POST"])
def add_module(request, pk):
    course = get_object_or_404(Course, pk=pk)
    if request.method == "POST":
        form = ModuleForm(request.POST, course=course)
        if form.is_valid():
            form.save()
            messages.success(request, "Modul qo‘shildi.")
            return redirect("course_detail", pk=course.pk)
        messages.error(request, "Formada xatolik bor.")
    else:
        form = ModuleForm(course=course)
    return render(
        request,
        "courses/course/module_form.html",
        {"form": form, "course": course},
    )


@role_required(CustomUser.Role.ADMIN, CustomUser.Role.TEACHER)
@require_http_methods(["GET", "POST"])
def add_lesson(request, pk, module_id):
    course = get_object_or_404(Course, pk=pk)
    module = get_object_or_404(Module, pk=module_id, course=course)
    if request.method == "POST":
        form = LessonForm(request.POST, module=module)
        if form.is_valid():
            form.save()
            messages.success(request, "Dars qo‘shildi.")
            return redirect("course_detail", pk=course.pk)
        messages.error(request, "Formada xatolik bor.")
    else:
        form = LessonForm(module=module)
    return render(
        request,
        "courses/course/lesson_form.html",
        {"form": form, "course": course, "module": module},
    )


list_course = course_list
create_course = course_create
