from django.contrib import admin

from .models import Cart, Category, MenuItem, Order, OrderItem


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["id", "title", "slug"]
    prepopulated_fields = {"slug": ("title",)}


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ["id", "title", "price", "category", "featured"]
    list_filter = ["category", "featured"]


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ["id", "user", "delivery_crew", "status", "total", "date"]
    list_filter = ["status", "date"]
    inlines = [OrderItemInline]


admin.site.register(Cart)
