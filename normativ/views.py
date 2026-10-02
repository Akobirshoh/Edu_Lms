from collections import defaultdict

from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from accounts.decorators import role_required, staff_roles
from accounts.models import CustomUser, StudentProfile
from courses.models import GroupStudent, Lesson
from normativ.forms import (
    AnswerSubmitForm,
    GradeForm,
    NormativForm,
    NormativQuestionFormSet,
)
from normativ.models import Normativ, NormativAnswer
from normativ.services import award_normativ_coins


def _student_in_lesson_course(student, lesson):
    return GroupStudent.objects.filter(
        student=student,
        is_active=True,
        group__course=lesson.module.course,
    ).exists()


def _teacher_owns_student(user, student):
    if user.is_superuser or user.role == CustomUser.Role.ADMIN:
        return True
    if user.role == CustomUser.Role.TEACHER and hasattr(user, 'teacher_profile'):
        return GroupStudent.objects.filter(
            student=student,
            is_active=True,
            group__teacher=user.teacher_profile,
        ).exists()
    if user.role == CustomUser.Role.MENTOR:
        return GroupStudent.objects.filter(
            student=student,
            is_active=True,
            group__mentor=user,
        ).exists()
    return False


@staff_roles
def create_normativ(request, lesson_id):
    lesson = get_object_or_404(Lesson.objects.select_related('module__course'), pk=lesson_id)

    if request.method == 'POST':
        form = NormativForm(request.POST)
        formset = NormativQuestionFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            normativ = form.save(commit=False)
            normativ.lesson = lesson
            normativ.save()
            formset.instance = normativ
            formset.save()
            messages.success(request, "Normativ yaratildi.")
            return redirect('create_normativ', lesson_id=lesson.pk)
    else:
        form = NormativForm()
        formset = NormativQuestionFormSet()

    normativs = Normativ.objects.filter(lesson=lesson).prefetch_related('questions')
    return render(request, 'normativ/create.html', {
        'form': form,
        'formset': formset,
        'lesson': lesson,
        'normativs': normativs,
    })


@role_required(CustomUser.Role.STUDENT)
def student_submit(request, normativ_id):
    normativ = get_object_or_404(
        Normativ.objects.select_related('lesson__module__course').prefetch_related('questions'),
        pk=normativ_id,
    )
    student = get_object_or_404(StudentProfile, user=request.user)

    if not _student_in_lesson_course(student, normativ.lesson):
        messages.error(request, "Bu normativga ruxsat yo'q.")
        return redirect('student_results')

    questions = list(normativ.questions.all())
    existing_qs = NormativAnswer.objects.filter(student=student, question__in=questions)
    existing = {a.question_id: a for a in existing_qs}
    all_submitted = len(existing) == len(questions) and len(questions) > 0

    if request.method == 'POST' and not all_submitted:
        form = AnswerSubmitForm(request.POST, questions=questions, existing=existing)
        if form.is_valid():
            for question, text in form.cleaned_answers().items():
                NormativAnswer.objects.get_or_create(
                    question=question,
                    student=student,
                    defaults={'answer_text': text},
                )
            messages.success(request, "Javoblar topshirildi.")
            return redirect('student_submit', normativ_id=normativ.pk)
    else:
        form = AnswerSubmitForm(questions=questions, existing=existing)

    return render(request, 'normativ/submit.html', {
        'normativ': normativ,
        'form': form,
        'existing': existing,
        'all_submitted': all_submitted,
    })


@staff_roles
def teacher_queue(request):
    answers = NormativAnswer.objects.filter(score__isnull=True).select_related(
        'student__user',
        'question__normativ__lesson',
    )

    if request.user.role == CustomUser.Role.TEACHER and hasattr(request.user, 'teacher_profile'):
        student_ids = GroupStudent.objects.filter(
            is_active=True,
            group__teacher=request.user.teacher_profile,
        ).values_list('student_id', flat=True)
        answers = answers.filter(student_id__in=student_ids)
    elif request.user.role == CustomUser.Role.MENTOR:
        student_ids = GroupStudent.objects.filter(
            is_active=True,
            group__mentor=request.user,
        ).values_list('student_id', flat=True)
        answers = answers.filter(student_id__in=student_ids)

    grouped = defaultdict(list)
    for answer in answers.order_by('student__user__last_name', 'question__order'):
        key = (answer.student_id, answer.question.normativ_id)
        grouped[key].append(answer)

    queue = []
    for (student_id, normativ_id), items in grouped.items():
        first = items[0]
        queue.append({
            'student': first.student,
            'normativ': first.question.normativ,
            'answers': items,
            'count': len(items),
        })

    return render(request, 'normativ/queue.html', {'queue': queue})


@staff_roles
def grade_answers(request, normativ_id, student_id):
    normativ = get_object_or_404(Normativ.objects.prefetch_related('questions'), pk=normativ_id)
    student = get_object_or_404(StudentProfile, pk=student_id)

    if not _teacher_owns_student(request.user, student):
        messages.error(request, "Bu o'quvchi javoblariga ruxsat yo'q.")
        return redirect('teacher_queue')

    answers = list(
        NormativAnswer.objects.filter(
            student=student,
            question__normativ=normativ,
        ).select_related('question').order_by('question__order')
    )
    if not answers:
        messages.error(request, "Javoblar topilmadi.")
        return redirect('teacher_queue')

    if request.method == 'POST':
        form = GradeForm(request.POST, answers=answers)
        if form.is_valid():
            total = 0
            now = timezone.now()
            for item in form.cleaned_grades():
                answer = item['answer']
                answer.score = item['score']
                answer.feedback = item['feedback']
                answer.checked_by = request.user
                answer.checked_at = now
                answer.save(update_fields=['score', 'feedback', 'checked_by', 'checked_at', 'updated_at'])
                total += item['score']
            award_normativ_coins(student, normativ, total, request.user)
            messages.success(request, "Baholar saqlandi.")
            return redirect('teacher_queue')
    else:
        form = GradeForm(answers=answers)

    return render(request, 'normativ/grade.html', {
        'form': form,
        'normativ': normativ,
        'student': student,
        'answers': answers,
    })


@role_required(CustomUser.Role.STUDENT)
def student_results(request):
    student = get_object_or_404(StudentProfile, user=request.user)
    answers = (
        NormativAnswer.objects.filter(student=student)
        .select_related('question__normativ', 'checked_by')
        .order_by('-created_at')
    )

    by_normativ = defaultdict(lambda: {'answers': [], 'score': 0, 'max_score': 0, 'pending': False})
    for answer in answers:
        bucket = by_normativ[answer.question.normativ_id]
        bucket['normativ'] = answer.question.normativ
        bucket['answers'].append(answer)
        bucket['max_score'] += answer.question.max_score
        if answer.score is None:
            bucket['pending'] = True
        else:
            bucket['score'] += answer.score
        if 'date' not in bucket or answer.created_at > bucket['date']:
            bucket['date'] = answer.created_at

    results = sorted(by_normativ.values(), key=lambda x: x['date'], reverse=True)
    return render(request, 'normativ/results.html', {
        'results': results,
        'answers': answers,
    })
