from decimal import Decimal

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import filters, generics, status
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Cart, Category, MenuItem, Order, OrderItem
from .permissions import in_group
from .serializers import (
    CartSerializer,
    CategorySerializer,
    GroupMembershipSerializer,
    MenuItemSerializer,
    OrderSerializer,
    UserSummarySerializer,
)


User = get_user_model()


class CategoryListView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    pagination_class = None

    def get_permissions(self):
        return [IsAdminUser()] if self.request.method == "POST" else [AllowAny()]


class MenuItemListView(generics.ListCreateAPIView):
    serializer_class = MenuItemSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["title", "category__title"]
    ordering_fields = ["price", "title"]

    def get_queryset(self):
        queryset = MenuItem.objects.select_related("category").all()
        category = self.request.query_params.get("category")
        if category:
            queryset = queryset.filter(category_id=category)
        return queryset

    def get_permissions(self):
        return [IsAdminUser()] if self.request.method == "POST" else [AllowAny()]


class MenuItemDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = MenuItem.objects.select_related("category").all()
    serializer_class = MenuItemSerializer

    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]
        return [IsAuthenticated()]

    def _can_manage(self):
        return self.request.user.is_staff or in_group(self.request.user, "Manager")

    def update(self, request, *args, **kwargs):
        if not self._can_manage():
            return Response(status=status.HTTP_403_FORBIDDEN)
        if in_group(request.user, "Manager") and not request.user.is_staff:
            disallowed = set(request.data) - {"featured"}
            if disallowed:
                return Response(
                    {"detail": "Managers may only update the featured field."},
                    status=status.HTTP_403_FORBIDDEN,
                )
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return Response(status=status.HTTP_403_FORBIDDEN)
        return super().destroy(request, *args, **kwargs)


class GroupUsersView(APIView):
    permission_classes = [IsAuthenticated]
    group_name = ""

    def _allowed(self, request):
        if self.group_name == "Manager":
            return request.user.is_staff
        return request.user.is_staff or in_group(request.user, "Manager")

    def get(self, request):
        if not self._allowed(request):
            return Response(status=status.HTTP_403_FORBIDDEN)
        group, _ = Group.objects.get_or_create(name=self.group_name)
        users = User.objects.filter(groups=group).order_by("username")
        return Response(UserSummarySerializer(users, many=True).data)

    def post(self, request):
        if not self._allowed(request):
            return Response(status=status.HTTP_403_FORBIDDEN)
        serializer = GroupMembershipSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        group, _ = Group.objects.get_or_create(name=self.group_name)
        user = serializer.validated_data["user"]
        user.groups.add(group)
        return Response(UserSummarySerializer(user).data, status=status.HTTP_201_CREATED)


class ManagerUsersView(GroupUsersView):
    group_name = "Manager"


class DeliveryCrewUsersView(GroupUsersView):
    group_name = "Delivery crew"


class GroupUserDetailView(APIView):
    permission_classes = [IsAuthenticated]
    group_name = ""

    def delete(self, request, pk):
        allowed = request.user.is_staff or (
            self.group_name == "Delivery crew" and in_group(request.user, "Manager")
        )
        if not allowed:
            return Response(status=status.HTTP_403_FORBIDDEN)
        user = get_object_or_404(User, pk=pk)
        group = get_object_or_404(Group, name=self.group_name)
        user.groups.remove(group)
        return Response(status=status.HTTP_204_NO_CONTENT)


class ManagerUserDetailView(GroupUserDetailView):
    group_name = "Manager"


class DeliveryCrewUserDetailView(GroupUserDetailView):
    group_name = "Delivery crew"


class CartView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        items = Cart.objects.filter(user=request.user).select_related(
            "menuitem", "menuitem__category"
        )
        return Response(CartSerializer(items, many=True).data)

    def post(self, request):
        serializer = CartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        menuitem = serializer.validated_data["menuitem"]
        quantity = serializer.validated_data["quantity"]
        cart_item, created = Cart.objects.get_or_create(
            user=request.user,
            menuitem=menuitem,
            defaults={"quantity": quantity, "unit_price": menuitem.price, "price": 0},
        )
        if not created:
            cart_item.quantity = quantity
        cart_item.save()
        response_status = status.HTTP_201_CREATED if created else status.HTTP_200_OK
        return Response(CartSerializer(cart_item).data, status=response_status)

    def delete(self, request):
        Cart.objects.filter(user=request.user).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class OrderListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        orders = Order.objects.prefetch_related("items__menuitem__category").select_related(
            "user", "delivery_crew"
        )
        if request.user.is_staff or in_group(request.user, "Manager"):
            pass
        elif in_group(request.user, "Delivery crew"):
            orders = orders.filter(delivery_crew=request.user)
        else:
            orders = orders.filter(user=request.user)
        return Response(OrderSerializer(orders, many=True).data)

    @transaction.atomic
    def post(self, request):
        cart_items = list(
            Cart.objects.select_for_update()
            .filter(user=request.user)
            .select_related("menuitem")
        )
        if not cart_items:
            return Response(
                {"detail": "Your cart is empty."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        total = sum((item.price for item in cart_items), Decimal("0.00"))
        order = Order.objects.create(user=request.user, total=total)
        OrderItem.objects.bulk_create(
            [
                OrderItem(
                    order=order,
                    menuitem=item.menuitem,
                    quantity=item.quantity,
                    unit_price=item.unit_price,
                    price=item.price,
                )
                for item in cart_items
            ]
        )
        Cart.objects.filter(user=request.user).delete()
        order = Order.objects.prefetch_related("items__menuitem__category").get(pk=order.pk)
        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)


class OrderDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def _get_visible_order(self, request, pk):
        queryset = Order.objects.select_related("user", "delivery_crew").prefetch_related(
            "items__menuitem__category"
        )
        if request.user.is_staff or in_group(request.user, "Manager"):
            return get_object_or_404(queryset, pk=pk)
        if in_group(request.user, "Delivery crew"):
            return get_object_or_404(queryset, pk=pk, delivery_crew=request.user)
        return get_object_or_404(queryset, pk=pk, user=request.user)

    def get(self, request, pk):
        return Response(OrderSerializer(self._get_visible_order(request, pk)).data)

    def patch(self, request, pk):
        order = self._get_visible_order(request, pk)
        if request.user.is_staff or in_group(request.user, "Manager"):
            if "delivery_crew_id" in request.data:
                crew = get_object_or_404(User, pk=request.data["delivery_crew_id"])
                if not in_group(crew, "Delivery crew"):
                    return Response(
                        {"delivery_crew_id": "User is not in the Delivery crew group."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                order.delivery_crew = crew
            if "status" in request.data:
                order.status = bool(request.data["status"])
            order.save(update_fields=["delivery_crew", "status"])
        elif in_group(request.user, "Delivery crew"):
            if set(request.data) - {"status"}:
                return Response(status=status.HTTP_403_FORBIDDEN)
            order.status = bool(request.data.get("status", order.status))
            order.save(update_fields=["status"])
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)
        return Response(OrderSerializer(order).data)

    def delete(self, request, pk):
        if not (request.user.is_staff or in_group(request.user, "Manager")):
            return Response(status=status.HTTP_403_FORBIDDEN)
        self._get_visible_order(request, pk).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
