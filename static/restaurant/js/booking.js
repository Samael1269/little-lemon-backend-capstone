const form = document.getElementById("booking-form");
const dateInput = document.getElementById("id_reservation_date");
const slotInput = document.getElementById("id_reservation_slot");
const bookingsList = document.getElementById("bookings-list");
const bookingHeading = document.getElementById("booking-heading");
const formMessage = document.getElementById("form-message");

function localToday() {
  const now = new Date();
  const offset = now.getTimezoneOffset() * 60000;
  return new Date(now - offset).toISOString().slice(0, 10);
}

function hourLabel(hour) {
  const suffix = hour >= 12 ? "PM" : "AM";
  const displayHour = hour > 12 ? hour - 12 : hour;
  return `${displayHour} ${suffix}`;
}

async function refreshBookings() {
  const selectedDate = dateInput.value;
  bookingHeading.textContent = `Bookings for ${selectedDate}`;
  const response = await fetch(`/bookings?date=${encodeURIComponent(selectedDate)}`);
  const bookings = await response.json();
  const bookedSlots = new Set(bookings.map((booking) => booking.fields.reservation_slot));

  for (const option of slotInput.options) {
    const isBooked = bookedSlots.has(Number(option.value));
    option.disabled = isBooked;
    option.textContent = `${hourLabel(Number(option.value))}${isBooked ? " — Booked" : ""}`;
  }
  if (slotInput.selectedOptions[0]?.disabled) {
    const firstAvailable = Array.from(slotInput.options).find((option) => !option.disabled);
    if (firstAvailable) slotInput.value = firstAvailable.value;
  }

  bookingsList.replaceChildren();
  if (!bookings.length) {
    const empty = document.createElement("p");
    empty.textContent = "No Booking";
    bookingsList.append(empty);
    return;
  }
  for (const booking of bookings) {
    const row = document.createElement("p");
    row.textContent = `${booking.fields.first_name} — ${hourLabel(booking.fields.reservation_slot)}`;
    bookingsList.append(row);
  }
}

dateInput.value = dateInput.value || localToday();
dateInput.min = localToday();
dateInput.addEventListener("change", refreshBookings);

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  formMessage.textContent = "";
  const csrfToken = form.querySelector("[name=csrfmiddlewaretoken]").value;
  const payload = {
    first_name: document.getElementById("id_first_name").value,
    reservation_date: dateInput.value,
    reservation_slot: slotInput.value,
  };
  const response = await fetch("/book/", {
    method: "POST",
    headers: {"Content-Type": "application/json", "X-CSRFToken": csrfToken},
    body: JSON.stringify(payload),
  });
  const result = await response.json();
  if (!response.ok) {
    formMessage.textContent = result.error || "Please check the form and try again.";
    return;
  }
  formMessage.textContent = "Reservation confirmed.";
  document.getElementById("id_first_name").value = "";
  await refreshBookings();
});

refreshBookings().catch(() => {
  bookingsList.textContent = "Bookings could not be loaded.";
});
