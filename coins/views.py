from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Sum
from django.db.models.functions import Coalesce
from django.shortcuts import get_object_or_404, redirect, render

from accounts.decorators import role_required, staff_roles
from accounts.models import CustomUser, StudentProfile
from coins.forms import ManualCoinForm, ShopItemForm
from coins.models import CoinTransaction, Purchase, ShopItem
from coins.services import PurchaseError, purchase_item_atomic


@role_required(CustomUser.Role.STUDENT)
def coin_history(request):
    student = get_object_or_404(StudentProfile, user=request.user)
    qs = CoinTransaction.objects.filter(student=student).select_related('created_by')
    paginator = Paginator(qs, 20)
    page = paginator.get_page(request.GET.get('page'))
    return render(request, 'coins/history.html', {
        'student': student,
        'page_obj': page,
        'balance': student.coin_balance,
    })


@role_required(
    CustomUser.Role.ADMIN,
    CustomUser.Role.TEACHER,
    CustomUser.Role.MENTOR,
    CustomUser.Role.STUDENT,
)
def leaderboard(request):
    students = (
        StudentProfile.objects.select_related('user')
        .annotate(balance=Coalesce(Sum('coin_transactions__amount'), 0))
        .order_by('-balance', 'user__last_name', 'user__first_name')
    )
    current_student = None
    current_rank = None
    if hasattr(request.user, 'student_profile'):
        current_student = request.user.student_profile
        for idx, s in enumerate(students, start=1):
            if s.pk == current_student.pk:
                current_rank = idx
                break

    return render(request, 'coins/leaderboard.html', {
        'students': students,
        'current_student': current_student,
        'current_rank': current_rank,
    })


@role_required(
    CustomUser.Role.ADMIN,
    CustomUser.Role.TEACHER,
    CustomUser.Role.MENTOR,
    CustomUser.Role.STUDENT,
)
def shop_list(request):
    items = ShopItem.objects.filter(is_active=True, stock__gt=0)
    balance = None
    if hasattr(request.user, 'student_profile'):
        balance = request.user.student_profile.coin_balance
    return render(request, 'coins/shop_list.html', {
        'items': items,
        'balance': balance,
    })


@staff_roles
def shop_create(request):
    if request.method == 'POST':
        form = ShopItemForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Mahsulot qo'shildi.")
            return redirect('shop_list')
    else:
        form = ShopItemForm()
    return render(request, 'coins/shop_form.html', {'form': form})


@role_required(CustomUser.Role.STUDENT)
def purchase_item(request, item_id):
    if request.method != 'POST':
        return redirect('shop_list')

    student = get_object_or_404(StudentProfile, user=request.user)
    item = get_object_or_404(ShopItem, pk=item_id)
    try:
        purchase_item_atomic(student, item, created_by=request.user)
        messages.success(request, "Xarid amalga oshirildi.")
    except PurchaseError as exc:
        messages.error(request, str(exc))
    except ShopItem.DoesNotExist:
        messages.error(request, "Mahsulot topilmadi.")
    return redirect('shop_list')


@role_required(
    CustomUser.Role.ADMIN,
    CustomUser.Role.TEACHER,
    CustomUser.Role.MENTOR,
    CustomUser.Role.STUDENT,
)
def purchases_list(request):
    if request.user.role == CustomUser.Role.STUDENT:
        student = get_object_or_404(StudentProfile, user=request.user)
        purchases = Purchase.objects.filter(student=student).select_related('item', 'student__user')
    else:
        purchases = Purchase.objects.select_related('item', 'student__user').all()
    return render(request, 'coins/purchases.html', {'purchases': purchases})


@staff_roles
def mark_delivered(request, purchase_id):
    if request.method != 'POST':
        return redirect('purchases_list')

    purchase = get_object_or_404(Purchase, pk=purchase_id)
    purchase.status = Purchase.Status.DELIVERED
    purchase.save(update_fields=['status', 'updated_at'])
    messages.success(request, "Xarid berildi deb belgilandi.")
    return redirect('purchases_list')


@staff_roles
def manual_coin(request):
    if request.method == 'POST':
        form = ManualCoinForm(request.POST)
        if form.is_valid():
            CoinTransaction.objects.create(
                student=form.cleaned_data['student'],
                amount=form.cleaned_data['amount'],
                reason=CoinTransaction.Reason.MANUAL,
                comment=form.cleaned_data.get('comment') or '',
                created_by=request.user,
            )
            messages.success(request, "Coin yozildi.")
            return redirect('manual_coin')
    else:
        form = ManualCoinForm()
    return render(request, 'coins/manual.html', {'form': form})
