from django.contrib import admin

from .models import Booking, Menu


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ["first_name", "reservation_date", "reservation_slot"]
    list_filter = ["reservation_date"]


admin.site.register(Menu)
