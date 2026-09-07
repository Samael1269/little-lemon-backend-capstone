from django import forms

from .models import Booking


class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ["first_name", "reservation_date", "reservation_slot"]
        labels = {
            "first_name": "First name",
            "reservation_date": "Reservation date",
            "reservation_slot": "Reservation slot",
        }
        widgets = {
            "first_name": forms.TextInput(attrs={"placeholder": "Your Name"}),
            "reservation_date": forms.DateInput(attrs={"type": "date"}),
            "reservation_slot": forms.Select(
                choices=[(hour, f"{hour}:00") for hour in range(10, 21)]
            ),
        }
