# Smart Car Rental

A Django-based car rental management platform with customer booking, fleet management, document verification, rental operations, reporting and a **simulated payment workflow**.

## Important payment scope

Payment is intentionally **simulation-only** in this release. The payment portion has not been replaced with a live gateway and should remain unchanged unless the project owner explicitly requests a payment change.

## Rental operations

Staff can now manage the complete operational handover:

1. Review and approve a booking.
2. Verify customer documents.
3. Confirm the simulated payment is paid.
4. Open Rental Operations.
5. Record pickup mileage, fuel and notes.
6. Start the active rental.
7. Record return mileage, fuel, notes and damage.
8. Optionally record a separate operational extra charge.
9. Complete the rental.

Pickup/return inspection records and extra charges are retained as auditable records.

## Fleet and availability

- Fleet status is operational: Available, Maintenance or Inactive.
- Reserved/rented quantity is derived from booking states.
- Booking approval uses a database transaction and row locking to protect the last available fleet unit from concurrent approvals.
- Historical bookings are retained rather than deleted.

## Security improvements

- Staff operations remain staff-only.
- State-changing operations use POST requests and CSRF protection.
- Customer document access is permission-checked through the protected document view.
- Uploaded customer documents are restricted to PDF/JPG/JPEG/PNG/WEBP and 10 MB.
- Production settings require an explicit SECRET_KEY and enable secure cookie/HSTS settings when DEBUG=False.

## Local setup

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic --noinput
python manage.py runserver
```

SQLite is used by default. To use PostgreSQL, set `DATABASE_URL` in `.env`.

## Tests

Run:

```powershell
python manage.py test
```

The suite includes authentication, booking lifecycle, availability, permissions, simulated payments, rental lifecycle and rental inspection/extra-charge operations.

## Production checklist

- Set `DEBUG=False`.
- Set a strong random `SECRET_KEY`.
- Set `ALLOWED_HOSTS` and `CSRF_TRUSTED_ORIGINS`.
- Configure PostgreSQL with `DATABASE_URL`.
- Configure persistent media storage for customer documents.
- Run migrations and `collectstatic`.
- Serve the application behind HTTPS and a production WSGI server.
- Back up the database and uploaded documents.
