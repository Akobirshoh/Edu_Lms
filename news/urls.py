from django.urls import path

from news import views

urlpatterns = [
    path('', views.news_list, name='news_list'),
    path('create/', views.news_create, name='news_create'),
    path('<int:pk>/', views.news_detail, name='news_detail'),
    path('<int:pk>/update/', views.news_update, name='news_update'),
]
