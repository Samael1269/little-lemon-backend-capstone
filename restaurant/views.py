import json
from datetime import date

from django.core import serializers
from django.db import IntegrityError, transaction
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from .forms import BookingForm
from .models import Booking, Menu


def home(request):
    return render(request, "index.html")


def about(request):
    return render(request, "about.html")


def menu(request):
    return render(request, "menu.html", {"menu": Menu.objects.all()})


@require_http_methods(["GET", "POST"])
def book(request):
    if request.method == "GET":
        return render(
            request,
            "book.html",
            {"form": BookingForm(initial={"reservation_date": date.today()})},
        )

    try:
        payload = json.loads(request.body or "{}")
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON data."}, status=400)

    if Booking.objects.filter(
        reservation_date=payload.get("reservation_date"),
        reservation_slot=payload.get("reservation_slot"),
    ).exists():
        return JsonResponse(
            {"error": "This reservation slot is already booked for that date."},
            status=409,
        )

    form = BookingForm(payload)
    if not form.is_valid():
        return JsonResponse({"errors": form.errors.get_json_data()}, status=400)

    try:
        with transaction.atomic():
            booking = form.save()
    except IntegrityError:
        return JsonResponse(
            {"error": "This reservation slot is already booked for that date."},
            status=409,
        )

    return JsonResponse(
        {
            "id": booking.pk,
            "first_name": booking.first_name,
            "reservation_date": booking.reservation_date.isoformat(),
            "reservation_slot": booking.reservation_slot,
        },
        status=201,
    )


def reservations(request):
    return render(request, "reservations.html")


@require_http_methods(["GET"])
def bookings(request):
    queryset = Booking.objects.all()
    requested_date = request.GET.get("date")
    if requested_date:
        queryset = queryset.filter(reservation_date=requested_date)
    data = serializers.serialize("json", queryset)
    return HttpResponse(data, content_type="application/json")
