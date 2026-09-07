import json
from datetime import date

from django.db import IntegrityError, transaction
from django.test import TestCase
from django.urls import reverse

from .models import Booking


class BookingAssessmentTests(TestCase):
    def setUp(self):
        self.booking = Booking.objects.create(
            first_name="Jimmy Doe",
            reservation_date=date(2026, 12, 13),
            reservation_slot=19,
        )

    def test_booking_page_has_three_fields_and_date_picker(self):
        response = self.client.get(reverse("book"))
        self.assertContains(response, 'id="id_first_name"')
        self.assertContains(response, 'id="id_reservation_date"')
        self.assertContains(response, 'id="id_reservation_slot"')
        self.assertContains(response, 'type="date"')

    def test_bookings_api_lists_all_and_filters_by_date(self):
        Booking.objects.create(
            first_name="Jane Doe",
            reservation_date=date(2026, 12, 14),
            reservation_slot=17,
        )
        all_response = self.client.get("/bookings")
        filtered_response = self.client.get("/bookings?date=2026-12-13")
        self.assertEqual(len(json.loads(all_response.content)), 2)
        filtered = json.loads(filtered_response.content)
        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0]["fields"]["first_name"], "Jimmy Doe")

    def test_duplicate_date_and_slot_is_rejected_by_database(self):
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Booking.objects.create(
                    first_name="Duplicate",
                    reservation_date=self.booking.reservation_date,
                    reservation_slot=self.booking.reservation_slot,
                )

    def test_json_booking_creation_and_duplicate_response(self):
        payload = {
            "first_name": "New Guest",
            "reservation_date": "2026-12-15",
            "reservation_slot": 18,
        }
        response = self.client.post(
            "/book/", data=json.dumps(payload), content_type="application/json"
        )
        self.assertEqual(response.status_code, 201)
        duplicate = self.client.post(
            "/book/", data=json.dumps(payload), content_type="application/json"
        )
        self.assertEqual(duplicate.status_code, 409)

    def test_pages_and_static_javascript_are_connected(self):
        self.assertEqual(self.client.get(reverse("home")).status_code, 200)
        self.assertEqual(self.client.get(reverse("reservations")).status_code, 200)
        with open("static/restaurant/js/booking.js", encoding="utf-8") as file:
            script = file.read()
        self.assertIn("fetch(`/bookings?date=", script)
        self.assertIn('textContent = "No Booking"', script)
        self.assertIn('dateInput.addEventListener("change"', script)
        self.assertIn("localToday()", script)
