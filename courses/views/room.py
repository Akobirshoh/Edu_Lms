from django.contrib import messages
from django.db.models import ProtectedError
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from accounts.decorators import role_required
from accounts.models import CustomUser
from courses.forms.room import RoomForm
from courses.models import Room


@role_required(CustomUser.Role.ADMIN, CustomUser.Role.TEACHER)
@require_http_methods(["GET", "POST"])
def room_list(request):
    rooms = Room.objects.order_by("name")
    if request.method == "POST":
        form = RoomForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Xona yaratildi.")
            return redirect("room_list")
        messages.error(request, "Formada xatolik bor.")
    else:
        form = RoomForm()
    return render(
        request,
        "courses/room/list.html",
        {"rooms": rooms, "form": form},
    )


@role_required(CustomUser.Role.ADMIN, CustomUser.Role.TEACHER)
@require_http_methods(["GET", "POST"])
def room_update(request, pk):
    room = get_object_or_404(Room, pk=pk)
    if request.method == "POST":
        form = RoomForm(request.POST, instance=room)
        if form.is_valid():
            form.save()
            messages.success(request, "Xona yangilandi.")
            return redirect("room_list")
        messages.error(request, "Formada xatolik bor.")
    else:
        form = RoomForm(instance=room)
    return render(
        request,
        "courses/room/create.html",
        {"form": form, "room": room},
    )


@role_required(CustomUser.Role.ADMIN, CustomUser.Role.TEACHER)
@require_http_methods(["GET", "POST"])
def room_delete(request, pk):
    room = get_object_or_404(Room, pk=pk)
    if request.method == "POST":
        try:
            room.delete()
        except ProtectedError:
            messages.error(
                request,
                "Bu xonani o‘chirib bo‘lmaydi: jadvalda ishlatilmoqda.",
            )
            return redirect("room_list")
        messages.success(request, "Xona o‘chirildi.")
        return redirect("room_list")
    return render(request, "courses/room/delete.html", {"room": room})


list_rooms = room_list
create_room = room_list
delete_room = room_delete
