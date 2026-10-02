from django.urls import path

from coins import views

urlpatterns = [
    path('history/', views.coin_history, name='coin_history'),
    path('leaderboard/', views.leaderboard, name='leaderboard'),
    path('shop/', views.shop_list, name='shop_list'),
    path('shop/create/', views.shop_create, name='shop_create'),
    path('shop/<int:item_id>/buy/', views.purchase_item, name='purchase_item'),
    path('purchases/', views.purchases_list, name='purchases_list'),
    path('purchases/<int:purchase_id>/deliver/', views.mark_delivered, name='mark_delivered'),
    path('manual/', views.manual_coin, name='manual_coin'),
]
