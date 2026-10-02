from django.urls import path

from accounts.views import teacher, user

urlpatterns = [
    path("", user.home, name="home"),
    path("login/", user.login_view, name="login"),
    path("logout/", user.logout_view, name="logout"),
    path("profile/", user.profile_view, name="profile"),
    path("profile/edit/", user.profile_edit, name="profile_edit"),
    path("register/", user.register_view, name="register"),
    path("teachers/", teacher.teacher_list, name="teacher_list"),
    path("teachers/<int:pk>/", teacher.teacher_profile, name="teacher_detail"),
    path("teacher/profile/", teacher.teacher_profile, name="teacher_profile"),
    path("teacher/profile/edit/", teacher.teacher_edit, name="teacher_edit"),
    path("teacher/groups/", teacher.my_groups, name="teacher_groups"),
]

urlpatterns += [
    path("teachers/", teacher.teacher_list, name="teacher"),
    path("teacher/profile/edit/", teacher.teacher_edit, name="edit_teacher"),
    path("teacher/groups/", teacher.my_groups, name="get_my_groups"),
]
