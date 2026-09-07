from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Cart, Category, MenuItem, Order, OrderItem


User = get_user_model()


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "slug", "title"]


class MenuItemSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        source="category",
        queryset=Category.objects.all(),
        write_only=True,
    )

    class Meta:
        model = MenuItem
        fields = ["id", "title", "price", "featured", "category", "category_id"]


class CartSerializer(serializers.ModelSerializer):
    menuitem = MenuItemSerializer(read_only=True)
    menuitem_id = serializers.PrimaryKeyRelatedField(
        source="menuitem",
        queryset=MenuItem.objects.all(),
        write_only=True,
    )
    unit_price = serializers.DecimalField(max_digits=6, decimal_places=2, read_only=True)
    price = serializers.DecimalField(max_digits=8, decimal_places=2, read_only=True)

    class Meta:
        model = Cart
        fields = ["id", "menuitem", "menuitem_id", "quantity", "unit_price", "price"]


class OrderItemSerializer(serializers.ModelSerializer):
    menuitem = MenuItemSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = ["id", "menuitem", "quantity", "unit_price", "price"]


class UserSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email"]


class OrderSerializer(serializers.ModelSerializer):
    user = UserSummarySerializer(read_only=True)
    delivery_crew = UserSummarySerializer(read_only=True)
    delivery_crew_id = serializers.PrimaryKeyRelatedField(
        source="delivery_crew",
        queryset=User.objects.all(),
        allow_null=True,
        required=False,
        write_only=True,
    )
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = [
            "id",
            "user",
            "delivery_crew",
            "delivery_crew_id",
            "status",
            "total",
            "date",
            "items",
        ]
        read_only_fields = ["total", "date"]


class GroupMembershipSerializer(serializers.Serializer):
    user_id = serializers.PrimaryKeyRelatedField(
        source="user",
        queryset=User.objects.all(),
        required=False,
    )
    username = serializers.CharField(required=False)

    def validate(self, attrs):
        if attrs.get("user"):
            return attrs
        username = attrs.get("username")
        if not username:
            raise serializers.ValidationError("Provide user_id or username.")
        try:
            attrs["user"] = User.objects.get(username=username)
        except User.DoesNotExist as exc:
            raise serializers.ValidationError({"username": "User not found."}) from exc
        return attrs
