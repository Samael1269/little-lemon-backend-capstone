# Little Lemon Back-End Capstone API

This Django REST Framework project provides static Little Lemon pages, table-booking functionality, menu APIs, user registration, token authentication, role-based access, carts, orders, and unit tests. The submitted settings default to MySQL, while `USE_SQLITE_FOR_TESTS=1` is available only for automated verification on machines without MySQL.

## MySQL setup

Create the database by running `setup_mysql.sql`, then set the values shown in `.env.example` for your local MySQL account. On PowerShell, for example:

```text
$env:MYSQL_DATABASE="littlelemon"
$env:MYSQL_USER="root"
$env:MYSQL_PASSWORD="your password"
```

## Run the project

```text
cd littlelemon
pipenv install
pipenv shell
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```

Open these pages:

- Home: `http://127.0.0.1:8000/`
- Booking form: `http://127.0.0.1:8000/book/`
- Reservations: `http://127.0.0.1:8000/reservations/`
- All bookings JSON: `http://127.0.0.1:8000/bookings`
- Date-filtered JSON: `http://127.0.0.1:8000/bookings?date=2026-12-13`

Capstone API endpoints:

- Categories: `http://127.0.0.1:8000/api/categories`
- Menu items: `http://127.0.0.1:8000/api/menu-items`
- Cart: `http://127.0.0.1:8000/api/cart/menu-items`
- Orders: `http://127.0.0.1:8000/api/orders`
- Registration: `http://127.0.0.1:8000/auth/users/`
- Token login: `http://127.0.0.1:8000/auth/token/login/`

The booking form selects the current date, refreshes reservations when the date changes, disables occupied time slots, uses `fetch()` for API requests, and displays `No Booking` when a date has no reservations. A database uniqueness constraint also prevents duplicate date-and-slot reservations.

## Verify without a local MySQL server

```text
$env:USE_SQLITE_FOR_TESTS="1"
python manage.py test
```
