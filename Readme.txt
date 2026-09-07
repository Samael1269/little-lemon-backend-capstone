Little Lemon Back-End Capstone API
==================================

Project setup
-------------
1. Install the dependencies with: pipenv install
2. Activate the environment with: pipenv shell
3. Configure the MySQL connection using the variables in .env.example.
4. Run: python manage.py migrate
5. Run: python manage.py runserver

Pages and API paths for peer review
-----------------------------------
Static home page:
http://127.0.0.1:8000/

Booking page:
http://127.0.0.1:8000/book/

Reservations page:
http://127.0.0.1:8000/reservations/

Bookings API:
http://127.0.0.1:8000/bookings

Bookings filtered by date:
http://127.0.0.1:8000/bookings?date=2026-12-13

API endpoints:
http://127.0.0.1:8000/api/categories
http://127.0.0.1:8000/api/menu-items
http://127.0.0.1:8000/api/cart/menu-items
http://127.0.0.1:8000/api/orders

Authentication endpoints:
http://127.0.0.1:8000/auth/users/
http://127.0.0.1:8000/auth/token/login/
http://127.0.0.1:8000/auth/token/logout/

Tests
-----
Run all unit tests with: python manage.py test

The API can be tested with Insomnia. Protected endpoints require an
Authorization header in the form: Token <authentication-token>
