from functools import wraps

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect

from accounts.models import CustomUser


def role_required(*roles):
    def decorator(view_func):
        @login_required
        @wraps(view_func)
        def _wrapped(request, *args, **kwargs):
            if request.user.role not in roles and not request.user.is_superuser:
                messages.error(request, "Bu sahifaga ruxsat yo‘q.")
                return redirect("home")
            return view_func(request, *args, **kwargs)

        return _wrapped

    return decorator


def staff_roles(view_func):
    return role_required(
        CustomUser.Role.ADMIN,
        CustomUser.Role.TEACHER,
        CustomUser.Role.MENTOR,
    )(view_func)


def admin_required(view_func):
    return role_required(CustomUser.Role.ADMIN)(view_func)
