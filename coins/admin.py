from django.contrib import admin

from .models import CoinTransaction, Purchase, ShopItem


@admin.register(CoinTransaction)
class CoinTransactionAdmin(admin.ModelAdmin):
    list_display = ("student", "amount", "reason", "created_by", "created_at")
    list_filter = ("reason",)
    search_fields = ("student__user__username", "comment")
    readonly_fields = ("student", "amount", "reason", "comment", "created_by", "created_at", "updated_at")

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(ShopItem)
class ShopItemAdmin(admin.ModelAdmin):
    list_display = ("name", "price", "stock", "is_active")
    list_filter = ("is_active",)


@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    list_display = ("student", "item", "status", "created_at")
    list_filter = ("status",)
    readonly_fields = ("transaction",)
