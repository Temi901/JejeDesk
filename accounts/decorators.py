from functools import wraps

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied


def owner_required(view):
    @wraps(view)
    @login_required
    def wrapper(request, *args, **kwargs):
        user = request.user
        if user.business_id is None or user.role != user.Role.OWNER:
            raise PermissionDenied
        return view(request, *args, **kwargs)

    return wrapper
