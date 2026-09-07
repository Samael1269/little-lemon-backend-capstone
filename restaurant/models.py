from django.db import models


class Booking(models.Model):
    first_name = models.CharField(max_length=200)
    reservation_date = models.DateField()
    reservation_slot = models.PositiveSmallIntegerField()

    class Meta:
        ordering = ["reservation_date", "reservation_slot"]
        constraints = [
            models.UniqueConstraint(
                fields=["reservation_date", "reservation_slot"],
                name="unique_reservation_date_and_slot",
            )
        ]

    def __str__(self):
        return f"{self.first_name} - {self.reservation_date} at {self.reservation_slot}:00"


class Menu(models.Model):
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    menu_item_description = models.TextField(max_length=1000, default="")

    def __str__(self):
        return self.name
