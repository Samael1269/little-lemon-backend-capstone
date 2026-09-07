from rest_framework.permissions import BasePermission


def in_group(user, group_name):
    return bool(
        user
        and user.is_authenticated
        and user.groups.filter(name=group_name).exists()
    )


class IsManager(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_superuser or in_group(request.user, "Manager")


class IsDeliveryCrew(BasePermission):
    def has_permission(self, request, view):
        return in_group(request.user, "Delivery crew")
