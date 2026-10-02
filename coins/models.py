from django.conf import settings
from django.db import models

from accounts.models import StudentProfile, TimeStampedModel


class CoinTransaction(TimeStampedModel):
    class Reason(models.TextChoices):
        ATTENDANCE = 'attendance', 'Davomat'
        NORMATIV = 'normativ', 'Normativ'
        PURCHASE = 'purchase', 'Xarid'
        MANUAL = 'manual', "Qo'lda"

    student = models.ForeignKey(StudentProfile, on_delete=models.PROTECT, related_name='coin_transactions')
    amount = models.IntegerField()
    reason = models.CharField(max_length=15, choices=Reason.choices)
    comment = models.CharField(max_length=255, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='given_transactions',
    )

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.student}: {self.amount:+d} ({self.get_reason_display()})'


class ShopItem(TimeStampedModel):
    name = models.CharField(max_length=200)
    image = models.ImageField(upload_to='shop/', blank=True)
    price = models.PositiveIntegerField()
    stock = models.PositiveSmallIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.name} ({self.price} coin)'


class Purchase(TimeStampedModel):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Kutilmoqda'
        DELIVERED = 'delivered', 'Berildi'

    student = models.ForeignKey(StudentProfile, on_delete=models.PROTECT, related_name='purchases')
    item = models.ForeignKey(ShopItem, on_delete=models.PROTECT, related_name='purchases')
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    transaction = models.OneToOneField(CoinTransaction, on_delete=models.PROTECT, related_name='purchase')

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.student} — {self.item.name}'
