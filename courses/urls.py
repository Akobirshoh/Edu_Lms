from django.urls import path

from courses.views import course, group, room

urlpatterns = [
    path("", course.course_list, name="course_list"),
    path("create/", course.course_create, name="course_create"),
    path("<int:pk>/", course.course_detail, name="course_detail"),
    path("<int:pk>/update/", course.course_update, name="course_update"),
    path("<int:pk>/delete/", course.course_delete, name="course_delete"),
    path("<int:pk>/modules/add/", course.add_module, name="module_add"),
    path(
        "<int:pk>/modules/<int:module_id>/lessons/add/",
        course.add_lesson,
        name="lesson_add",
    ),
    path("rooms/", room.room_list, name="room_list"),
    path("rooms/<int:pk>/update/", room.room_update, name="room_update"),
    path("rooms/<int:pk>/delete/", room.room_delete, name="room_delete"),
    path("groups/", group.group_list, name="group_list"),
    path("groups/create/", group.group_create, name="group_create"),
    path("groups/<int:pk>/", group.group_detail, name="group_detail"),
    path("groups/<int:pk>/update/", group.group_update, name="group_update"),
    path(
        "groups/<int:group_id>/students/",
        group.group_students_manage,
        name="group_students_manage",
    ),
]

urlpatterns += [
    path("", course.course_list, name="list_course"),
    path("create/", course.course_create, name="create_course"),
    path("rooms/", room.room_list, name="rooms"),
    path("rooms/", room.room_list, name="room-create"),
    path("rooms/<int:pk>/update/", room.room_update, name="room-update"),
    path("rooms/<int:pk>/delete/", room.room_delete, name="room-delete"),
    path("groups/", group.group_list, name="group-list"),
    path("groups/create/", group.group_create, name="group-create"),
    path(
        "groups/<int:group_id>/students/",
        group.group_students_manage,
        name="group-students-manage",
    ),
]
