from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand
from rest_framework.authtoken.models import Token

from LittleLemonAPI.models import Category, MenuItem


USERS = {
    "admin": {"password": "AdminPass123!", "email": "admin@example.com"},
    "manager": {"password": "ManagerPass123!", "email": "manager@example.com"},
    "delivery": {"password": "DeliveryPass123!", "email": "delivery@example.com"},
    "customer": {"password": "CustomerPass123!", "email": "customer@example.com"},
}


class Command(BaseCommand):
    help = "Create peer-review groups, demo users, tokens, and menu data."

    def handle(self, *args, **options):
        User = get_user_model()
        manager_group, _ = Group.objects.get_or_create(name="Manager")
        crew_group, _ = Group.objects.get_or_create(name="Delivery crew")

        users = {}
        for username, details in USERS.items():
            user, _ = User.objects.get_or_create(
                username=username, defaults={"email": details["email"]}
            )
            user.email = details["email"]
            user.set_password(details["password"])
            if username == "admin":
                user.is_staff = True
                user.is_superuser = True
            user.save()
            users[username] = user
            Token.objects.get_or_create(user=user)

        users["manager"].groups.add(manager_group)
        users["delivery"].groups.add(crew_group)

        mains, _ = Category.objects.get_or_create(
            slug="mains", defaults={"title": "Mains"}
        )
        desserts, _ = Category.objects.get_or_create(
            slug="desserts", defaults={"title": "Desserts"}
        )
        MenuItem.objects.get_or_create(
            title="Greek Salad",
            defaults={"price": "12.50", "category": mains, "featured": True},
        )
        MenuItem.objects.get_or_create(
            title="Lemon Dessert",
            defaults={"price": "8.00", "category": desserts},
        )
        self.stdout.write(self.style.SUCCESS("Demo users and menu data are ready."))
