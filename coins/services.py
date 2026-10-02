from django.db import transaction
from django.db.models import F

from coins.models import CoinTransaction, Purchase, ShopItem


class PurchaseError(Exception):
    pass


def purchase_item_atomic(student, item, created_by=None):
    with transaction.atomic():
        locked = ShopItem.objects.select_for_update().get(pk=item.pk)

        if not locked.is_active:
            raise PurchaseError("Mahsulot faol emas.")
        if locked.stock < 1:
            raise PurchaseError("Mahsulot tugagan.")

        balance = student.coin_balance
        if balance < locked.price:
            raise PurchaseError("Coin yetarli emas.")

        tx = CoinTransaction.objects.create(
            student=student,
            amount=-locked.price,
            reason=CoinTransaction.Reason.PURCHASE,
            comment=locked.name,
            created_by=created_by,
        )
        purchase = Purchase.objects.create(
            student=student,
            item=locked,
            transaction=tx,
            status=Purchase.Status.PENDING,
        )
        locked.stock = F('stock') - 1
        locked.save(update_fields=['stock', 'updated_at'])
        locked.refresh_from_db(fields=['stock'])
        return purchase
