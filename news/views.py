from django.contrib import messages
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from accounts.decorators import role_required, staff_roles
from accounts.models import CustomUser
from news.forms import NewsForm
from news.models import News


@role_required(
    CustomUser.Role.ADMIN,
    CustomUser.Role.TEACHER,
    CustomUser.Role.MENTOR,
    CustomUser.Role.STUDENT,
)
def news_list(request):
    qs = News.objects.select_related('author').filter(is_published=True)
    if request.user.is_authenticated:
        qs = News.objects.select_related('author').filter(
            Q(is_published=True) | Q(author=request.user)
        )
    return render(request, 'news/list.html', {'news_list': qs})


@role_required(
    CustomUser.Role.ADMIN,
    CustomUser.Role.TEACHER,
    CustomUser.Role.MENTOR,
    CustomUser.Role.STUDENT,
)
def news_detail(request, pk):
    news = get_object_or_404(News.objects.select_related('author'), pk=pk)
    if not news.is_published and news.author_id != request.user.id and not (
        request.user.is_superuser or request.user.role == CustomUser.Role.ADMIN
    ):
        messages.error(request, "Yangilik topilmadi.")
        return redirect('news_list')
    return render(request, 'news/detail.html', {'news': news})


@staff_roles
def news_create(request):
    if request.method == 'POST':
        form = NewsForm(request.POST, request.FILES)
        if form.is_valid():
            news = form.save(commit=False)
            news.author = request.user
            news.save()
            messages.success(request, "Yangilik saqlandi.")
            return redirect('news_detail', pk=news.pk)
    else:
        form = NewsForm()
    return render(request, 'news/form.html', {'form': form})


@staff_roles
def news_update(request, pk):
    news = get_object_or_404(News, pk=pk)
    is_admin = request.user.is_superuser or request.user.role == CustomUser.Role.ADMIN
    if news.author_id != request.user.id and not is_admin:
        messages.error(request, "Bu yangilikni tahrirlashga ruxsat yo'q.")
        return redirect('news_list')

    if request.method == 'POST':
        form = NewsForm(request.POST, request.FILES, instance=news)
        if form.is_valid():
            form.save()
            messages.success(request, "Yangilik yangilandi.")
            return redirect('news_detail', pk=news.pk)
    else:
        form = NewsForm(instance=news)
    return render(request, 'news/form.html', {'form': form, 'news': news})
