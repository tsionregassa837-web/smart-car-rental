import datetime
from decimal import Decimal
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from core.models import Booking, Car, Contact, RentalInspection, ExtraCharge


class SmartCarRentalTestCase(TestCase):
    """
    Base test case with helper fixtures for users, cars, and bookings.
    """

    def setUp(self):
        self.client = Client()

        # Regular customer
        self.customer = User.objects.create_user(
            username="customer1",
            email="customer1@example.com",
            password="SecureCustomerPass123!",
            first_name="Abebe",
            last_name="Kebede",
        )

        # Another customer (for authorization tests)
        self.other_customer = User.objects.create_user(
            username="customer2",
            email="customer2@example.com",
            password="SecureCustomerPass123!",
            first_name="Almaz",
            last_name="Ayele",
        )

        # Staff user
        self.staff_user = User.objects.create_user(
            username="staff1",
            email="staff1@example.com",
            password="SecureStaffPass123!",
            is_staff=True,
        )

        # Create test vehicles
        dummy_img = SimpleUploadedFile(
            "test_car.jpg",
            b"\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff\x00\x00\x00\x21\xf9\x04\x01\x00\x00\x00\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x44\x01\x00\x3b",
            content_type="image/jpeg",
        )

        self.car = Car.objects.create(
            name="Toyota Corolla 2025",
            model_year=2025,
            total_quantity=3,
            price_per_day=Decimal("2500.00"),
            image=dummy_img,
            plate_number="ET-1001",
            fleet_status="Available",
            transmission="Automatic",
            fuel_type="Petrol",
            seats=5,
            doors=4,
            features="Bluetooth, USB, Backup Camera",
        )

        self.single_car = Car.objects.create(
            name="Mercedes-Benz C200",
            model_year=2024,
            total_quantity=1,
            price_per_day=Decimal("6000.00"),
            image=dummy_img,
            plate_number="ET-2002",
            fleet_status="Available",
            transmission="Automatic",
            fuel_type="Petrol",
            seats=5,
            doors=4,
        )

        self.dummy_license = SimpleUploadedFile(
            "license.pdf",
            b"%PDF-1.4 test driver license",
            content_type="application/pdf",
        )

        self.dummy_id = SimpleUploadedFile(
            "national_id.pdf",
            b"%PDF-1.4 test national id",
            content_type="application/pdf",
        )


class UserAuthTests(SmartCarRentalTestCase):

    def test_registration_success(self):
        response = self.client.post(
            reverse("register"),
            {
                "username": "newuser",
                "email": "newuser@example.com",
                "first_name": "Tadesse",
                "last_name": "Haile",
                "password": "StrongPassword123!",
                "confirm_password": "StrongPassword123!",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username="newuser").exists())

    def test_registration_duplicate_username_fails(self):
        response = self.client.post(
            reverse("register"),
            {
                "username": "customer1",
                "email": "diff@example.com",
                "password": "StrongPassword123!",
                "confirm_password": "StrongPassword123!",
            },
        )
        self.assertEqual(response.status_code, 200)

    def test_registration_password_mismatch_fails(self):
        response = self.client.post(
            reverse("register"),
            {
                "username": "mismatchuser",
                "email": "mismatch@example.com",
                "password": "StrongPassword123!",
                "confirm_password": "DifferentPassword123!",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username="mismatchuser").exists())

    def test_login_success(self):
        response = self.client.post(
            reverse("login"),
            {
                "username": "customer1",
                "password": "SecureCustomerPass123!",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn("_auth_user_id", self.client.session)

    def test_login_invalid_credentials_fails(self):
        response = self.client.post(
            reverse("login"),
            {
                "username": "customer1",
                "password": "WrongPassword!",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_logout(self):
        self.client.login(
            username="customer1", password="SecureCustomerPass123!"
        )
        response = self.client.get(reverse("logout"))
        self.assertEqual(response.status_code, 302)
        self.assertNotIn("_auth_user_id", self.client.session)


class FleetAndCarModelTests(SmartCarRentalTestCase):

    def test_feature_list_property(self):
        features = self.car.feature_list
        self.assertIn("Bluetooth", features)
        self.assertIn("USB", features)
        self.assertIn("Backup Camera", features)

    def test_available_quantity_without_bookings(self):
        self.assertEqual(self.car.available_quantity, 3)

    def test_available_quantity_with_approved_and_active_bookings(self):
        today = timezone.localdate()
        Booking.objects.create(
            user=self.customer,
            car=self.car,
            car_type=self.car.name,
            pickup_date=today + datetime.timedelta(days=2),
            dropoff_date=today + datetime.timedelta(days=5),
            pickup_location="Addis Ababa Airport",
            first_name="Abebe",
            last_name="Kebede",
            email="customer1@example.com",
            driver_license=self.dummy_license,
            national_id=self.dummy_id,
            document_status="Verified",
            status="Approved",
            total_price=Decimal("7500.00"),
        )
        self.assertEqual(self.car.available_quantity, 2)

    def test_maintenance_car_has_zero_availability(self):
        self.car.fleet_status = "Maintenance"
        self.car.maintenance_reason = "Brake inspection"
        self.car.save()
        self.assertEqual(self.car.available_quantity, 0)

    def test_inactive_car_has_zero_availability(self):
        self.car.fleet_status = "Inactive"
        self.car.save()
        self.assertEqual(self.car.available_quantity, 0)

    def test_available_for_dates(self):
        today = timezone.localdate()
        p1 = today + datetime.timedelta(days=5)
        d1 = today + datetime.timedelta(days=10)

        Booking.objects.create(
            user=self.customer,
            car=self.single_car,
            car_type=self.single_car.name,
            pickup_date=p1,
            dropoff_date=d1,
            pickup_location="Bole",
            first_name="Abebe",
            last_name="Kebede",
            email="customer1@example.com",
            driver_license=self.dummy_license,
            national_id=self.dummy_id,
            document_status="Verified",
            status="Approved",
            total_price=Decimal("30000.00"),
        )

        # Overlapping query
        avail_overlap = self.single_car.available_for_dates(
            p1 + datetime.timedelta(days=1), d1 + datetime.timedelta(days=2)
        )
        self.assertEqual(avail_overlap, 0)

        # Non-overlapping future query
        avail_non_overlap = self.single_car.available_for_dates(
            d1 + datetime.timedelta(days=1), d1 + datetime.timedelta(days=5)
        )
        self.assertEqual(avail_non_overlap, 1)


class BookingLifecycleTests(SmartCarRentalTestCase):

    def test_create_valid_booking(self):
        today = timezone.localdate()
        pickup = today + datetime.timedelta(days=1)
        dropoff = today + datetime.timedelta(days=4)

        booking = Booking(
            user=self.customer,
            car=self.car,
            car_type=self.car.name,
            pickup_date=pickup,
            dropoff_date=dropoff,
            pickup_location="Bole Airport",
            first_name="Abebe",
            last_name="Kebede",
            email="customer1@example.com",
            phone="+251911223344",
            driver_license=self.dummy_license,
            national_id=self.dummy_id,
        )
        booking.full_clean()
        booking.save()

        self.assertEqual(booking.status, "Pending")
        self.assertEqual(booking.rental_days, 3)
        self.assertEqual(booking.total_price, Decimal("7500.00"))

    def test_past_pickup_date_fails_validation(self):
        today = timezone.localdate()
        booking = Booking(
            user=self.customer,
            car=self.car,
            car_type=self.car.name,
            pickup_date=today - datetime.timedelta(days=2),
            dropoff_date=today + datetime.timedelta(days=2),
            pickup_location="Bole",
            first_name="Abebe",
            last_name="Kebede",
            email="customer1@example.com",
        )
        with self.assertRaises(ValidationError):
            booking.full_clean()

    def test_dropoff_before_pickup_fails_validation(self):
        today = timezone.localdate()
        booking = Booking(
            user=self.customer,
            car=self.car,
            car_type=self.car.name,
            pickup_date=today + datetime.timedelta(days=5),
            dropoff_date=today + datetime.timedelta(days=3),
            pickup_location="Bole",
            first_name="Abebe",
            last_name="Kebede",
            email="customer1@example.com",
        )
        with self.assertRaises(ValidationError):
            booking.full_clean()


class DocumentAndApprovalTests(SmartCarRentalTestCase):

    def setUp(self):
        super().setUp()
        today = timezone.localdate()
        self.booking = Booking.objects.create(
            user=self.customer,
            car=self.car,
            car_type=self.car.name,
            pickup_date=today + datetime.timedelta(days=2),
            dropoff_date=today + datetime.timedelta(days=5),
            pickup_location="Addis Ababa",
            first_name="Abebe",
            last_name="Kebede",
            email="customer1@example.com",
            phone="+251911223344",
            driver_license=self.dummy_license,
            national_id=self.dummy_id,
            document_status="Pending",
            status="Pending",
        )

    def test_verify_documents_staff_post(self):
        self.client.login(username="staff1", password="SecureStaffPass123!")
        response = self.client.post(
            reverse("verify_documents", args=[self.booking.id, "verify"])
        )
        self.assertEqual(response.status_code, 302)
        self.booking.refresh_from_db()
        self.assertEqual(self.booking.document_status, "Verified")

    def test_approve_booking_with_verified_documents(self):
        self.booking.document_status = "Verified"
        self.booking.save()

        self.client.login(username="staff1", password="SecureStaffPass123!")
        response = self.client.post(
            reverse("update_booking_status", args=[self.booking.id, "Approved"])
        )
        self.assertEqual(response.status_code, 302)
        self.booking.refresh_from_db()
        self.assertEqual(self.booking.status, "Approved")

    def test_approve_booking_with_unverified_documents_fails(self):
        self.booking.document_status = "Pending"
        self.booking.save()

        self.client.login(username="staff1", password="SecureStaffPass123!")
        response = self.client.post(
            reverse("update_booking_status", args=[self.booking.id, "Approved"])
        )
        self.booking.refresh_from_db()
        self.assertEqual(self.booking.status, "Pending")

    def test_document_view_authorization(self):
        # Owner can view
        self.client.login(
            username="customer1", password="SecureCustomerPass123!"
        )
        resp_owner = self.client.get(
            reverse("booking_document", args=[self.booking.id, "license"])
        )
        self.assertEqual(resp_owner.status_code, 200)

        # Other customer is denied
        self.client.login(
            username="customer2", password="SecureCustomerPass123!"
        )
        resp_other = self.client.get(
            reverse("booking_document", args=[self.booking.id, "license"])
        )
        self.assertEqual(resp_other.status_code, 403)

        # Staff can view
        self.client.login(username="staff1", password="SecureStaffPass123!")
        resp_staff = self.client.get(
            reverse("booking_document", args=[self.booking.id, "license"])
        )
        self.assertEqual(resp_staff.status_code, 200)


class PaymentWorkflowTests(SmartCarRentalTestCase):

    def setUp(self):
        super().setUp()
        today = timezone.localdate()
        self.booking = Booking.objects.create(
            user=self.customer,
            car=self.car,
            car_type=self.car.name,
            pickup_date=today + datetime.timedelta(days=2),
            dropoff_date=today + datetime.timedelta(days=5),
            pickup_location="Addis Ababa",
            first_name="Abebe",
            last_name="Kebede",
            email="customer1@example.com",
            phone="+251911223344",
            driver_license=self.dummy_license,
            national_id=self.dummy_id,
            document_status="Verified",
            status="Approved",
            total_price=Decimal("7500.00"),
        )

    def test_cash_payment_selection_sets_pending(self):
        self.client.login(
            username="customer1", password="SecureCustomerPass123!"
        )
        response = self.client.post(
            reverse("payment", args=[self.booking.id]),
            {
                "payment_method": "Cash",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.booking.refresh_from_db()
        self.assertEqual(self.booking.payment_method, "Cash")
        self.assertEqual(self.booking.payment_status, "Pending")
        self.assertTrue(self.booking.payment_reference.startswith("CASH-"))

    def test_staff_confirm_cash_payment(self):
        self.booking.payment_method = "Cash"
        self.booking.payment_status = "Pending"
        self.booking.payment_reference = "CASH-TEST"
        self.booking.save()

        self.client.login(username="staff1", password="SecureStaffPass123!")
        response = self.client.post(
            reverse("mark_payment_paid", args=[self.booking.id])
        )
        self.assertEqual(response.status_code, 302)
        self.booking.refresh_from_db()
        self.assertEqual(self.booking.payment_status, "Paid")
        self.assertIsNotNone(self.booking.payment_date)

    def test_chapa_simulation_payment(self):
        self.client.login(
            username="customer1", password="SecureCustomerPass123!"
        )
        response = self.client.post(
            reverse("payment", args=[self.booking.id]),
            {
                "payment_method": "Chapa",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.booking.refresh_from_db()
        self.assertEqual(self.booking.payment_method, "Chapa")
        self.assertEqual(self.booking.payment_status, "Paid")
        self.assertTrue(self.booking.payment_reference.startswith("SIM-"))


class RentalLifecycleTests(SmartCarRentalTestCase):

    def setUp(self):
        super().setUp()
        today = timezone.localdate()
        self.booking = Booking.objects.create(
            user=self.customer,
            car=self.car,
            car_type=self.car.name,
            pickup_date=today + datetime.timedelta(days=2),
            dropoff_date=today + datetime.timedelta(days=5),
            pickup_location="Addis Ababa",
            first_name="Abebe",
            last_name="Kebede",
            email="customer1@example.com",
            phone="+251911223344",
            driver_license=self.dummy_license,
            national_id=self.dummy_id,
            document_status="Verified",
            status="Approved",
            payment_status="Paid",
            payment_method="Cash",
            payment_reference="CASH-PAID",
            total_price=Decimal("7500.00"),
        )

    def test_start_rental_success(self):
        self.client.login(username="staff1", password="SecureStaffPass123!")
        response = self.client.post(
            reverse("rental_action", args=[self.booking.id, "start"])
        )
        self.assertEqual(response.status_code, 302)
        self.booking.refresh_from_db()
        self.assertEqual(self.booking.status, "Active")
        self.assertIsNotNone(self.booking.pickup_completed)

    def test_start_rental_unpaid_fails(self):
        self.booking.payment_status = "Pending"
        self.booking.save()

        self.client.login(username="staff1", password="SecureStaffPass123!")
        response = self.client.post(
            reverse("rental_action", args=[self.booking.id, "start"])
        )
        self.booking.refresh_from_db()
        self.assertEqual(self.booking.status, "Approved")

    def test_complete_rental_success(self):
        self.booking.status = "Active"
        self.booking.pickup_completed = timezone.now()
        self.booking.save()

        self.client.login(username="staff1", password="SecureStaffPass123!")
        response = self.client.post(
            reverse("rental_action", args=[self.booking.id, "complete"])
        )
        self.assertEqual(response.status_code, 302)
        self.booking.refresh_from_db()
        self.assertEqual(self.booking.status, "Completed")
        self.assertIsNotNone(self.booking.return_completed)

    def test_cancel_booking_by_customer_post(self):
        today = timezone.localdate()
        pending_booking = Booking.objects.create(
            user=self.customer,
            car=self.car,
            car_type=self.car.name,
            pickup_date=today + datetime.timedelta(days=3),
            dropoff_date=today + datetime.timedelta(days=6),
            pickup_location="Addis Ababa",
            first_name="Abebe",
            last_name="Kebede",
            email="customer1@example.com",
            phone="+251911223344",
            driver_license=self.dummy_license,
            national_id=self.dummy_id,
            document_status="Pending",
            status="Pending",
        )

        self.client.login(
            username="customer1", password="SecureCustomerPass123!"
        )
        response = self.client.post(
            reverse("cancel_booking", args=[pending_booking.id])
        )
        self.assertEqual(response.status_code, 302)
        pending_booking.refresh_from_db()
        self.assertEqual(pending_booking.status, "Cancelled")


class SecurityAndPermissionsTests(SmartCarRentalTestCase):

    def test_non_staff_blocked_from_admin_dashboard(self):
        self.client.login(
            username="customer1", password="SecureCustomerPass123!"
        )
        response = self.client.get(reverse("admin_dashboard"))
        self.assertEqual(response.status_code, 302)

    def test_non_staff_blocked_from_booking_management(self):
        self.client.login(
            username="customer1", password="SecureCustomerPass123!"
        )
        response = self.client.get(reverse("booking_management"))
        self.assertEqual(response.status_code, 302)

    def test_non_staff_blocked_from_reports_dashboard(self):
        self.client.login(
            username="customer1", password="SecureCustomerPass123!"
        )
        response = self.client.get(reverse("reports_dashboard"))
        self.assertEqual(response.status_code, 302)

    def test_state_changing_actions_reject_get_requests(self):
        self.client.login(username="staff1", password="SecureStaffPass123!")
        today = timezone.localdate()
        booking = Booking.objects.create(
            user=self.customer,
            car=self.car,
            car_type=self.car.name,
            pickup_date=today + datetime.timedelta(days=2),
            dropoff_date=today + datetime.timedelta(days=5),
            pickup_location="Addis Ababa",
            first_name="Abebe",
            last_name="Kebede",
            email="customer1@example.com",
            phone="+251911223344",
            driver_license=self.dummy_license,
            national_id=self.dummy_id,
            document_status="Pending",
            status="Pending",
        )

        # GET to update_booking_status -> 405 Method Not Allowed
        resp1 = self.client.get(
            reverse("update_booking_status", args=[booking.id, "Approved"])
        )
        self.assertEqual(resp1.status_code, 405)

        # GET to rental_action -> 405 Method Not Allowed
        resp2 = self.client.get(
            reverse("rental_action", args=[booking.id, "start"])
        )
        self.assertEqual(resp2.status_code, 405)

        # GET to cancel_booking -> 405 Method Not Allowed
        resp3 = self.client.get(reverse("cancel_booking", args=[booking.id]))
        self.assertEqual(resp3.status_code, 405)


class RentalOperationsTests(SmartCarRentalTestCase):
    def setUp(self):
        super().setUp()
        today = timezone.localdate()
        self.booking = Booking.objects.create(
            user=self.customer, car=self.car, car_type=self.car.name,
            pickup_date=today + datetime.timedelta(days=2),
            dropoff_date=today + datetime.timedelta(days=5),
            pickup_location="Addis Ababa", first_name="Abebe",
            last_name="Kebede", email="customer1@example.com",
            phone="+251911223344", driver_license=self.dummy_license,
            national_id=self.dummy_id, document_status="Verified",
            status="Approved", payment_status="Paid", payment_method="Cash",
            payment_reference="CASH-OPS",
        )
        self.client.login(username="staff1", password="SecureStaffPass123!")

    def test_pickup_operation_records_inspection(self):
        response = self.client.post(reverse("rental_operations", args=[self.booking.id]), {
            "action":"pickup", "mileage":"12000", "fuel_level":"Full",
            "notes":"Clean vehicle", "damage_found":"", "damage_description":"",
        })
        self.assertEqual(response.status_code, 302)
        self.booking.refresh_from_db()
        self.assertEqual(self.booking.status, "Active")
        self.assertEqual(self.booking.pickup_mileage, 12000)
        self.assertTrue(RentalInspection.objects.filter(booking=self.booking, inspection_type="Pickup").exists())

    def test_return_operation_requires_valid_mileage_and_completes(self):
        self.booking.status="Active"
        self.booking.pickup_mileage=12000
        self.booking.pickup_completed=timezone.now()
        self.booking.save()
        response = self.client.post(reverse("rental_operations", args=[self.booking.id]), {
            "action":"return", "mileage":"12150", "fuel_level":"3/4",
            "notes":"Returned clean", "damage_found":"", "damage_description":"",
            "charge-charge_type":"Cleaning", "charge-description":"Interior cleaning", "charge-amount":"500",
        })
        self.assertEqual(response.status_code, 302)
        self.booking.refresh_from_db()
        self.assertEqual(self.booking.status, "Completed")
        self.assertEqual(self.booking.return_mileage, 12150)
        self.assertTrue(RentalInspection.objects.filter(booking=self.booking, inspection_type="Return").exists())
        self.assertEqual(ExtraCharge.objects.filter(booking=self.booking).count(), 1)

    def test_return_mileage_cannot_be_less_than_pickup(self):
        self.booking.status="Active"
        self.booking.pickup_mileage=12000
        self.booking.pickup_completed=timezone.now()
        self.booking.save()
        response = self.client.post(reverse("rental_operations", args=[self.booking.id]), {
            "action":"return", "mileage":"11000", "fuel_level":"Full",
            "notes":"", "damage_found":"", "damage_description":"",
        })
        self.assertEqual(response.status_code, 200)
        self.booking.refresh_from_db()
        self.assertEqual(self.booking.status, "Active")
