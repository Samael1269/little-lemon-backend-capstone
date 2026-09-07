fetch("/bookings")
  .then((response) => response.json())
  .then((bookings) => {
    document.getElementById("reservations-json").textContent = JSON.stringify(bookings, null, 2);
  })
  .catch(() => {
    document.getElementById("reservations-json").textContent = "Bookings could not be loaded.";
  });
