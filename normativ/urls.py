from django.urls import path

from normativ import views

urlpatterns = [
    path('lesson/<int:lesson_id>/create/', views.create_normativ, name='create_normativ'),
    path('<int:normativ_id>/submit/', views.student_submit, name='student_submit'),
    path('checking/', views.teacher_queue, name='teacher_queue'),
    path('<int:normativ_id>/grade/<int:student_id>/', views.grade_answers, name='grade_answers'),
    path('results/', views.student_results, name='student_results'),
]
