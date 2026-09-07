from django.urls import re_path

from . import views


urlpatterns = [
    re_path(r"^categories/?$", views.CategoryListView.as_view(), name="categories"),
    re_path(r"^menu-items/?$", views.MenuItemListView.as_view(), name="menu-items"),
    re_path(
        r"^menu-items/(?P<pk>\d+)/?$",
        views.MenuItemDetailView.as_view(),
        name="menu-item-detail",
    ),
    re_path(
        r"^groups/manager/users/?$",
        views.ManagerUsersView.as_view(),
        name="manager-users",
    ),
    re_path(
        r"^groups/manager/users/(?P<pk>\d+)/?$",
        views.ManagerUserDetailView.as_view(),
        name="manager-user-detail",
    ),
    re_path(
        r"^groups/delivery-crew/users/?$",
        views.DeliveryCrewUsersView.as_view(),
        name="delivery-users",
    ),
    re_path(
        r"^groups/delivery-crew/users/(?P<pk>\d+)/?$",
        views.DeliveryCrewUserDetailView.as_view(),
        name="delivery-user-detail",
    ),
    re_path(r"^cart/menu-items/?$", views.CartView.as_view(), name="cart"),
    re_path(r"^orders/?$", views.OrderListView.as_view(), name="orders"),
    re_path(
        r"^orders/(?P<pk>\d+)/?$",
        views.OrderDetailView.as_view(),
        name="order-detail",
    ),
]
