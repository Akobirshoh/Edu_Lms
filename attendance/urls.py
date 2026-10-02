from django.urls import path

from attendance import views

urlpatterns = [
    path('group/<int:group_id>/lesson/create/', views.create_group_lesson, name='create_group_lesson'),
    path('lesson/<int:group_lesson_id>/mark/', views.mark_attendance, name='mark_attendance'),
    path('group/<int:group_id>/journal/', views.group_journal, name='group_journal'),
]
