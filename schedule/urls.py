from django.urls import path

from schedule import views

urlpatterns = [
    path('', views.weekly_schedule, name='weekly_schedule'),
    path('group/<int:group_id>/create/', views.schedule_create, name='schedule_create'),
    path('group/<int:group_id>/<int:pk>/update/', views.schedule_update, name='schedule_update'),
    path('group/<int:group_id>/<int:pk>/delete/', views.schedule_delete, name='schedule_delete'),
]
