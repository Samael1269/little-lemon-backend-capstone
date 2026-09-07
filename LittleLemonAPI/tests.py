from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Cart, Category, MenuItem, Order


class LittleLemonAPITests(APITestCase):
    def setUp(self):
        User = get_user_model()
        self.admin = User.objects.create_superuser("admin", password="pass")
        self.manager = User.objects.create_user("manager", password="pass")
        self.delivery = User.objects.create_user("delivery", password="pass")
        self.customer = User.objects.create_user("customer", password="pass")
        self.other_customer = User.objects.create_user("other", password="pass")
        self.manager_group = Group.objects.create(name="Manager")
        self.crew_group = Group.objects.create(name="Delivery crew")
        self.manager.groups.add(self.manager_group)
        self.delivery.groups.add(self.crew_group)
        self.category = Category.objects.create(slug="mains", title="Mains")
        self.item = MenuItem.objects.create(
            title="Pasta", price="10.00", category=self.category
        )

    def login(self, user):
        self.client.force_authenticate(user)

    def test_public_can_browse_filter_sort_and_paginate_menu(self):
        for number in range(6):
            MenuItem.objects.create(
                title=f"Item {number}", price=number + 1, category=self.category
            )
        response = self.client.get(
            f"/api/menu-items?category={self.category.pk}&ordering=price&page=1"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 7)
        self.assertEqual(len(response.data["results"]), 5)

    def test_admin_manages_catalog_and_manager_group(self):
        self.login(self.admin)
        category_response = self.client.post(
            "/api/categories", {"slug": "drinks", "title": "Drinks"}
        )
        self.assertEqual(category_response.status_code, status.HTTP_201_CREATED)
        menu_response = self.client.post(
            "/api/menu-items",
            {"title": "Tea", "price": "3.50", "category_id": self.category.pk},
        )
        self.assertEqual(menu_response.status_code, status.HTTP_201_CREATED)
        group_response = self.client.post(
            "/api/groups/manager/users", {"user_id": self.other_customer.pk}
        )
        self.assertEqual(group_response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(self.other_customer.groups.filter(name="Manager").exists())

    def test_manager_features_item_and_assigns_delivery_user(self):
        self.login(self.manager)
        feature_response = self.client.patch(
            f"/api/menu-items/{self.item.pk}", {"featured": True}, format="json"
        )
        self.assertEqual(feature_response.status_code, status.HTTP_200_OK)
        crew_response = self.client.post(
            "/api/groups/delivery-crew/users", {"user_id": self.other_customer.pk}
        )
        self.assertEqual(crew_response.status_code, status.HTTP_201_CREATED)

    def test_customer_cart_order_and_order_isolation(self):
        self.login(self.customer)
        cart_response = self.client.post(
            "/api/cart/menu-items",
            {"menuitem_id": self.item.pk, "quantity": 2},
        )
        self.assertEqual(cart_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(self.client.get("/api/cart/menu-items").status_code, 200)
        order_response = self.client.post("/api/orders")
        self.assertEqual(order_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(order_response.data["total"], "20.00")
        self.assertFalse(Cart.objects.filter(user=self.customer).exists())
        self.login(self.other_customer)
        self.assertEqual(
            self.client.get(f"/api/orders/{order_response.data['id']}").status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_manager_assigns_order_and_delivery_completes_it(self):
        order = Order.objects.create(user=self.customer, total="10.00")
        self.login(self.manager)
        assign = self.client.patch(
            f"/api/orders/{order.pk}",
            {"delivery_crew_id": self.delivery.pk},
            format="json",
        )
        self.assertEqual(assign.status_code, status.HTTP_200_OK)
        self.login(self.delivery)
        assigned = self.client.get("/api/orders")
        self.assertEqual(len(assigned.data), 1)
        delivered = self.client.patch(
            f"/api/orders/{order.pk}", {"status": True}, format="json"
        )
        self.assertEqual(delivered.status_code, status.HTTP_200_OK)
        order.refresh_from_db()
        self.assertTrue(order.status)

    def test_customer_registration_and_token_login(self):
        register = self.client.post(
            "/auth/users/",
            {"username": "newcustomer", "password": "StrongPass123!"},
        )
        self.assertEqual(register.status_code, status.HTTP_201_CREATED)
        login = self.client.post(
            "/auth/token/login/",
            {"username": "newcustomer", "password": "StrongPass123!"},
        )
        self.assertEqual(login.status_code, status.HTTP_200_OK)
        self.assertIn("auth_token", login.data)

    def test_unauthorized_role_changes_are_forbidden(self):
        self.login(self.customer)
        self.assertEqual(
            self.client.post(
                "/api/groups/manager/users", {"user_id": self.customer.pk}
            ).status_code,
            status.HTTP_403_FORBIDDEN,
        )
        self.assertEqual(
            self.client.post(
                "/api/categories", {"slug": "x", "title": "X"}
            ).status_code,
            status.HTTP_403_FORBIDDEN,
        )
