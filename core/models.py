import re

from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.utils import timezone

def validate_ethiopian_phone(value):
    """
    Validate Ethiopian phone numbers.

    Accepted formats:
    09XXXXXXXX
    +2519XXXXXXXX
    2519XXXXXXXX
    """

    if not value:
        return

    value = value.strip()

    pattern = r"^(09\d{8}|\+2519\d{8}|2519\d{8})$"

    if not re.fullmatch(pattern, value):
        raise ValidationError(
            "Enter a valid Ethiopian phone number."
        )

class Contact(models.Model):
    name = models.CharField(max_length=100)

    email = models.EmailField()

    message = models.TextField()

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.name


class Car(models.Model):
    name = models.CharField(
        max_length=100
    )

    model_year = models.IntegerField()

    total_quantity = models.PositiveIntegerField(
        default=1
    )

    price_per_day = models.DecimalField(
        max_digits=8,
        decimal_places=2
    )

    image = models.ImageField(
        upload_to="cars/"
    )

    plate_number = models.CharField(
        max_length=20,
        unique=True,
        blank=True,
        null=True,
    )

    fleet_status = models.CharField(
        max_length=20,
        choices=[
            ("Available", "Available"),
            ("Rented", "Rented"),
            ("Maintenance", "Maintenance"),
            ("Inactive", "Inactive"),
        ],
        default="Available"
    )

    maintenance_reason = models.TextField(
        blank=True
    )

    maintenance_count = models.PositiveIntegerField(
        default=0
    )
    transmission = models.CharField(
        max_length=30,
        choices=[
            ("Automatic", "Automatic"),
            ("Manual", "Manual"),
        ],
        default="Automatic",
    )

    fuel_type = models.CharField(
        max_length=30,
        choices=[
            ("Petrol", "Petrol"),
            ("Diesel", "Diesel"),
            ("Hybrid", "Hybrid"),
            ("Electric", "Electric"),
        ],
        default="Petrol",
    )

    seats = models.PositiveIntegerField(
        default=5
    )

    doors = models.PositiveIntegerField(
        default=4
    )

    luggage_capacity = models.CharField(
        max_length=50,
        choices=[
        ("1 small bag", "1 small bag"),
        ("2 small bags", "2 small bags"),
        ("1 large bag", "1 large bag"),
        ("2 large bags", "2 large bags"),
        ("3 large bags", "3 large bags"),
        ("4 large bags", "4 large bags"),
        ("5+ large bags", "5+ large bags"),
    ],
        blank=True,
        help_text="Select the vehicle's luggage capacity."
    )

    air_conditioning = models.BooleanField(
        default=True
    )

    features = models.TextField(
        blank=True,
        help_text="Example: Bluetooth, USB, Rear Camera, Cruise Control"
    )
    @property
    def feature_list(self):
        """
        Convert comma-separated features into a clean list
        for customer-facing display.
        """
        if not self.features:
            return []

        return [
            feature.strip()
            for feature in self.features.split(",")
            if feature.strip()
            ]

    @property
    def available_quantity(self):
        """
        Return the number of vehicles currently available.

        Maintenance and inactive fleets have zero availability.

        Pending bookings do NOT reduce availability.

        Approved and Active bookings each consume one vehicle unit.
        """

        if self.fleet_status in [
            "Maintenance",
            "Inactive"
        ]:
            return 0

        rented = Booking.objects.filter(
            car=self,
            status__in=[
                "Approved",
                "Active"
            ]
        ).count()

        return max(
            self.total_quantity - rented,
            0
        )

    def update_fleet_status(self):
        """
        Automatically update fleet status based on availability.

        Maintenance and Inactive are controlled manually and
        must never be overwritten automatically.
        """

        if self.fleet_status in [
            "Maintenance",
            "Inactive"
        ]:
            return

        if self.available_quantity > 0:
            self.fleet_status = "Available"
        else:
            self.fleet_status = "Rented"

        self.save(
            update_fields=["fleet_status"]
        )

    def available_for_dates(
        self,
        pickup_date,
        dropoff_date
    ):
        """
        Return available quantity for a specific rental period.

        Only Approved and Active bookings reserve vehicles.
        """

        overlapping = Booking.objects.filter(
            car=self,
            status__in=[
                "Approved",
                "Active"
            ],
            pickup_date__lte=dropoff_date,
            dropoff_date__gte=pickup_date
        ).count()

        return max(
            self.total_quantity - overlapping,
            0
        )

    def __str__(self):
        return self.name


class Booking(models.Model):

    STATUS_CHOICES = [
        ("Pending", "Pending"),
        ("Approved", "Approved"),
        ("Active", "Active Rental"),
        ("Completed", "Completed"),
        ("Cancelled", "Cancelled"),
        ("Rejected", "Rejected"),
    ]

    DOCUMENT_STATUS_CHOICES = [
        ("Pending", "Pending"),
        ("Verified", "Verified"),
        ("Rejected", "Rejected"),
    ]

    PAYMENT_STATUS_CHOICES = [
        ("Pending", "Pending"),
        ("Paid", "Paid"),
        ("Failed", "Failed"),
        ("Refunded", "Refunded"),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    car = models.ForeignKey(
        "Car",
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    car_type = models.CharField(
        max_length=100
    )

    pickup_date = models.DateField()

    dropoff_date = models.DateField()

    pickup_completed = models.DateTimeField(
        null=True,
        blank=True
    )

    return_completed = models.DateTimeField(
        null=True,
        blank=True
    )

    pickup_location = models.CharField(
        max_length=100
    )

    first_name = models.CharField(
        max_length=100
    )

    middle_name = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    last_name = models.CharField(
        max_length=100
    )

    email = models.EmailField()

    phone = models.CharField(
            max_length=15,
            blank=True,
            null=True,
            validators=[
                RegexValidator(
                    regex=r"^\+?[0-9]{9,15}$",
                    message="Enter a valid phone number."
                )
            ]
    )

    driver_license = models.FileField(
        upload_to="documents/licenses/",
        blank=True,
        null=True
    )

    national_id = models.FileField(
        upload_to="documents/ids/",
        blank=True,
        null=True
    )

    document_status = models.CharField(
        max_length=20,
        choices=DOCUMENT_STATUS_CHOICES,
        default="Pending"
    )

    total_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    payment_status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default="Pending"
    )

    payment_method = models.CharField(
        max_length=50,
            choices=[
        ("Chapa", "Chapa"),
        ("Telebirr", "Telebirr"),
        ("Cash", "Cash"),
    ],

        blank=True,
        null=True
    )

    payment_reference = models.CharField(
        max_length=150,
        blank=True,
        null=True
    )

    payment_date = models.DateTimeField(
        null=True,
        blank=True
    )

    status = models.CharField(
        max_length=50,
        choices=STATUS_CHOICES,
        default="Pending"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.first_name} - {self.car_type}"

    @property
    def rental_days(self):
        if (
            self.pickup_date
            and self.dropoff_date
        ):
            return (
                self.dropoff_date
                - self.pickup_date
            ).days

        return 0

    def clean(self):
        """
        Central model-level validation.

        This protects the business rules even when
        a form or view is bypassed.

        IMPORTANT:
        Status-transition validation is intentionally
        located here because Django's full_clean()
        executes clean().
        """

        errors = {}

        today = timezone.now().date()

        # =================================================
        # DATE VALIDATION
        # =================================================

#
# Date rules apply to active/new bookings.
# Cancelled and Rejected bookings may contain
# historical dates and must still be saveable.
#

        if self.status not in ["Cancelled", "Rejected"]:
            if (
                self.pickup_date
                and self.pickup_date < today
                ):
                errors["pickup_date"] = (
                "Pickup date cannot be in the past."
                )

        if (
            self.pickup_date
            and self.dropoff_date
            and self.dropoff_date <= self.pickup_date
            ):
            errors["dropoff_date"] = (
                "Dropoff date must be after pickup date."
                )

        # =================================================
        # STATUS TRANSITION VALIDATION
        # =================================================

        if self.pk:

            previous = Booking.objects.filter(
                pk=self.pk
            ).first()

            if previous:

                allowed_transitions = {

                    "Pending": {
                        "Pending",
                        "Approved",
                        "Rejected",
                        "Cancelled",
                    },

                    "Approved": {
                        "Approved",
                        "Active",
                        "Cancelled",
                    },

                    "Active": {
                        "Active",
                        "Completed",
                    },

                    "Completed": {
                        "Completed",
                    },

                    "Cancelled": {
                        "Cancelled",
                    },

                    "Rejected": {
                        "Rejected",
                    },
                }

                allowed = allowed_transitions.get(
                    previous.status,
                    {previous.status}
                )

                if self.status not in allowed:

                    errors["status"] = (
                        "Invalid booking status transition: "
                        f"{previous.status} → {self.status}."
                    )

        # =================================================
        # CAR / FLEET VALIDATION
        # =================================================

        if (
            self.car
            and self.status in [
                "Pending",
                "Approved"
            ]
        ):

            if self.car.fleet_status in [
                "Maintenance",
                "Inactive"
            ]:

                errors["car"] = (
                    "This car is currently unavailable "
                    "for rental."
                )

        
        # =================================================
        # APPROVAL VALIDATION
        # =================================================

        if self.status == "Approved":

            if not self.driver_license:

                errors["driver_license"] = (
                    "Customer driver license is required "
                    "before approval."
                )

            if not self.national_id:

                errors["national_id"] = (
                    "Customer national ID is required "
                    "before approval."
                )

            if self.document_status != "Verified":

                errors["document_status"] = (
                    "Documents must be verified before "
                    "approving this booking."
                )

        # =================================================
        # ACTIVE RENTAL VALIDATION
        # =================================================

        if self.status == "Active":

            if self.payment_status != "Paid":

                errors["payment_status"] = (
                    "Booking must be paid before the "
                    "rental can become active."
                )

            if self.document_status != "Verified":

                errors["document_status"] = (
                    "Customer documents must be verified "
                    "before pickup."
                )

            if self.car:

                if self.car.fleet_status in [
                    "Maintenance",
                    "Inactive"
                ]:

                    errors["car"] = (
                        "This car is currently unavailable "
                        "for rental."
                    )

        # =================================================
        # COMPLETED RENTAL VALIDATION
        # =================================================

        if self.status == "Completed":

            if self.pickup_completed is None:

                errors["pickup_completed"] = (
                    "A rental must be picked up before "
                    "it can be completed."
                )

            if self.payment_status != "Paid":

                errors["payment_status"] = (
                    "Completed rentals must have "
                    "a paid booking."
                )

            if self.document_status != "Verified":

                errors["document_status"] = (
                    "Completed rentals must have "
                    "verified documents."
                )

        # =================================================
        # PAYMENT VALIDATION
        # =================================================

        if self.payment_status == "Paid":

            if not self.payment_reference:

                errors["payment_reference"] = (
                    "A payment reference is required "
                    "for a paid booking."
                )

            if not self.payment_method:

                errors["payment_method"] = (
                    "A payment method is required "
                    "for a paid booking."
                )

        # =================================================
        # OVERLAPPING BOOKING VALIDATION
        # =================================================

        if (
            self.car
            and self.pickup_date
            and self.dropoff_date
            and self.status in [
                "Pending",
                "Approved"
            ]
        ):

            overlapping_bookings = Booking.objects.filter(
                car=self.car,
                pickup_date__lte=self.dropoff_date,
                dropoff_date__gte=self.pickup_date,
                status__in=[
                    "Approved",
                    "Active"
                ],
            ).exclude(
                pk=self.pk
            )

            if (
                overlapping_bookings.count()
                >= self.car.total_quantity
            ):

                errors["car"] = (
                    "This car is not available "
                    "for the selected dates."
                )

        # =================================================
        # FINAL VALIDATION
        # =================================================

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):

        # =================================================
        # CALCULATE TOTAL PRICE
        # =================================================

        if (
            self.car
            and self.pickup_date
            and self.dropoff_date
        ):

            rental_days = (
                self.dropoff_date
                - self.pickup_date
            ).days

            self.total_price = (
                rental_days
                * self.car.price_per_day
            )

        # =================================================
        # REJECTED BOOKING
        # =================================================

        if self.status == "Rejected":

            self.document_status = "Rejected"

        # =================================================
        # CANCELLED BOOKING
        # =================================================

        if self.status == "Cancelled":

            if self.payment_status == "Pending":

                self.payment_method = None

                self.payment_reference = None

                self.payment_date = None

        # =================================================
        # PICKUP
        # =================================================

        if (
            self.status == "Active"
            and self.pickup_completed is None
        ):

            self.pickup_completed = timezone.now()

        # =================================================
        # RETURN
        # =================================================

        if (
            self.status == "Completed"
            and self.return_completed is None
        ):

            self.return_completed = timezone.now()

        # =================================================
        # PAYMENT DATE
        # =================================================

        if (
            self.payment_status == "Paid"
            and self.payment_date is None
        ):

            self.payment_date = timezone.now()

        # =================================================
        # VALIDATE EVERYTHING
        # =================================================

        self.full_clean()

        # =================================================
        # SAVE BOOKING
        # =================================================

        super().save(
            *args,
            **kwargs
        )

        # =================================================
        # UPDATE CAR FLEET STATUS
        # =================================================

        if self.car:

            self.car.refresh_from_db()

            self.car.update_fleet_status()

    def delete(self, *args, **kwargs):

        car = self.car

        super().delete(
            *args,
            **kwargs
        )

        if car:

            car.refresh_from_db()

            car.update_fleet_status()
