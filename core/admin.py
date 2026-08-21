from django.contrib import admin, messages
from django.utils import timezone
from django.utils.html import format_html
from django.urls import reverse
import uuid

from .models import Car, Booking, Contact

# ==========================================================
# CAR ADMIN
# ==========================================================

@admin.register(Car)
class CarAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "plate_number",
        "model_year",
        "transmission",
        "fuel_type",
        "seats",
        "fleet_status",
        "total_quantity",
        "available_now",
        "price_per_day",
    )

    list_editable = (
        "fleet_status",
    )

    list_filter = (
        "fleet_status",
        "transmission",
        "fuel_type",
        "model_year",
        "air_conditioning",
    )

    search_fields = (
        "name",
        "plate_number",
        "features",
    )

    readonly_fields = (
        "available_now",
    )

    fieldsets = (

        # ==================================================
        # BASIC VEHICLE INFORMATION
        # ==================================================

        (
            "Basic Vehicle Information",
            {
                "fields": (
                    "name",
                    "model_year",
                    "image",
                    "price_per_day",
                )
            }
        ),

        # ==================================================
        # VEHICLE SPECIFICATIONS
        # ==================================================

        (
            "Vehicle Specifications",
            {
                "fields": (
                    "transmission",
                    "fuel_type",
                    "seats",
                    "doors",
                    "luggage_capacity",
                    "air_conditioning",
                    "features",
                ),
                "description": (
                    "Enter the specifications customers should see "
                    "when viewing this vehicle."
                ),
            }
        ),

        # ==================================================
        # FLEET MANAGEMENT
        # ADMIN ONLY
        # ==================================================

        (
            "Fleet Management",
            {
                "fields": (
                    "plate_number",
                    "total_quantity",
                    "fleet_status",
                    "available_now",
                ),
                "description": (
                    "Fleet availability and operational status are "
                    "managed by staff."
                ),
            }
        ),

        # ==================================================
        # MAINTENANCE
        # ADMIN ONLY
        # ==================================================

        (
            "Maintenance Information",
            {
                "fields": (
                    "maintenance_count",
                    "maintenance_reason",
                ),
                "description": (
                    "Internal maintenance information. "
                    "This information is not displayed to customers."
                ),
            }
        ),
    )

    # ======================================================
    # AVAILABLE VEHICLES
    # ======================================================

    @admin.display(
        description="Available Cars",
        ordering="total_quantity",
    )
    def available_now(self, obj):
        return obj.available_quantity
# ==========================================================
# BOOKING ADMIN
# ==========================================================

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "user",
        "first_name",
        "last_name",
        "phone",
        "car",
        "pickup_date",
        "dropoff_date",
        "status",
        "document_status",
        "driver_license_link",
        "national_id_link",
        "payment_status",
        "payment_method",
        "total_price",
    )

    list_filter = (
        "status",
        "document_status",
        "payment_status",
        "payment_method",
        "pickup_date",
        "created_at",
    )

    search_fields = (
        "first_name",
        "last_name",
        "email",
        "phone",
        "car_type",
        "payment_reference",
    )

    readonly_fields = (
        "pickup_completed",
        "return_completed",
        "created_at",
        "total_price",
        "payment_date",
        "driver_license_link",
        "national_id_link",
    )

    actions = (
        "verify_documents",
        "reject_documents",
        "approve_bookings",
        "cancel_bookings",
        "confirm_payments",
        "start_rentals",
        "complete_rentals",
    )

    fieldsets = (

        # ==================================================
        # CUSTOMER
        # ==================================================

        (
            "Customer Information",
            {
                "fields": (
                    "user",
                    "first_name",
                    "middle_name",
                    "last_name",
                    "email",
                    "phone",
                )
            }
        ),

        # ==================================================
        # BOOKING
        # ==================================================

        (
            "Booking Information",
            {
                "fields": (
                    "car",
                    "car_type",
                    "pickup_date",
                    "dropoff_date",
                    "pickup_location",
                    "status",
                    "total_price",
                )
            }
        ),

        # ==================================================
        # DOCUMENTS
        # ==================================================

        (
            "Customer Documents",
            {
                "fields": (
                    "driver_license",
                    "national_id",
                    "driver_license_link",
                    "national_id_link",
                    "document_status",
                )
            }
        ),

        # ==================================================
        # PAYMENT
        # ==================================================

        (
            "Payment Information",
            {
                "fields": (
                    "payment_status",
                    "payment_method",
                    "payment_reference",
                    "payment_date",
                )
            }
        ),

        # ==================================================
        # RENTAL
        # ==================================================

        (
            "Rental Tracking",
            {
                "fields": (
                    "pickup_completed",
                    "return_completed",
                    "created_at",
                )
            }
        ),

    )

    # ======================================================
    # DOCUMENT LINKS
    # ======================================================

    def driver_license_link(self, obj):
        if obj.driver_license:
            url = reverse(
                "booking_document",
                args=[obj.id, "license"]
                )
            return format_html(
                '<a href="{}" target="_blank">'
                'View Driver License'
                '</a>',
                url
                )

        return "No document"

    driver_license_link.short_description = "Driver License"

    def national_id_link(self, obj):
        if obj.national_id:
            url = reverse(
                "booking_document",
                args=[obj.id, "national-id"]
                )

            return format_html(
                '<a href="{}" target="_blank">'
                'View National ID'
                '</a>',
                url
                )

        return "No document"

    national_id_link.short_description = "National ID"

    # ======================================================
    # VERIFY DOCUMENTS
    # ======================================================

    @admin.action(description="Verify customer documents")
    def verify_documents(self, request, queryset):

        verified = 0
        skipped = 0

        for booking in queryset:

            # Both documents must exist
            if (
                not booking.driver_license
                or not booking.national_id
            ):
                skipped += 1
                continue

            # Verify documents
            booking.document_status = "Verified"

            booking.save()

            verified += 1

        if verified:

            self.message_user(
                request,
                f"{verified} booking(s) documents verified successfully.",
                level=messages.SUCCESS,
            )

        if skipped:

            self.message_user(
                request,
                f"{skipped} booking(s) skipped because documents are missing.",
                level=messages.WARNING,
            )

    # ======================================================
    # REJECT DOCUMENTS / BOOKING
    # ======================================================

    @admin.action(description="Reject selected bookings")
    def reject_documents(self, request, queryset):

        rejected = 0
        skipped = 0

        for booking in queryset:

            # Do not modify completed or cancelled bookings
            if booking.status in [
                "Completed",
                "Cancelled",
            ]:
                skipped += 1
                continue

            booking.status = "Rejected"
            booking.document_status = "Rejected"

            booking.save()

            rejected += 1

        if rejected:

            self.message_user(
                request,
                f"{rejected} booking(s) rejected successfully.",
                level=messages.SUCCESS,
            )

        if skipped:

            self.message_user(
                request,
                f"{skipped} booking(s) skipped.",
                level=messages.WARNING,
            )

    # ======================================================
    # APPROVE BOOKINGS
    # ======================================================

    @admin.action(description="Approve selected bookings")
    def approve_bookings(self, request, queryset):

        approved = 0
        skipped = 0

        for booking in queryset:

            # Must still be Pending
            if booking.status != "Pending":
                skipped += 1
                continue

            # Documents must be verified
            if booking.document_status != "Verified":
                skipped += 1
                continue

            # Documents must exist
            if (
                not booking.driver_license
                or not booking.national_id
            ):
                skipped += 1
                continue

            # Car must exist
            if not booking.car:
                skipped += 1
                continue

            # Check fleet status
            if booking.car.fleet_status in [
                "Maintenance",
                "Inactive",
            ]:
                skipped += 1
                continue

            # Check date availability
            if (
                booking.car.available_for_dates(
                    booking.pickup_date,
                    booking.dropoff_date
                ) <= 0
            ):
                skipped += 1
                continue

            # Approve
            booking.status = "Approved"

            booking.save()

            approved += 1

        if approved:

            self.message_user(
                request,
                f"{approved} booking(s) approved successfully.",
                level=messages.SUCCESS,
            )

        if skipped:

            self.message_user(
                request,
                f"{skipped} booking(s) skipped. "
                f"Check documents, vehicle availability, "
                f"or current booking status.",
                level=messages.WARNING,
            )

    # ======================================================
    # CANCEL BOOKINGS
    # ======================================================

    @admin.action(description="Cancel selected bookings")
    def cancel_bookings(self, request, queryset):

        cancelled = 0
        skipped = 0

        for booking in queryset:

            # ==================================================
            # Cancellation is allowed ONLY from:
            #
            # Pending  -> Cancelled
            # Approved -> Cancelled
            #
            # These cannot be cancelled:
            #
            # Rejected
            # Active
            # Completed
            # Cancelled
            # ==================================================

            if booking.status not in ["Pending", "Approved"]:

                skipped += 1

                if booking.status == "Rejected":

                    self.message_user(
                        request,
                        f"Booking #{booking.id} cannot be cancelled "
                        f"because it has already been rejected.",
                        level=messages.WARNING,
                    )

                elif booking.status == "Active":

                    self.message_user(
                        request,
                        f"Booking #{booking.id} cannot be cancelled "
                        f"because the rental is currently active.",
                        level=messages.WARNING,
                    )

                elif booking.status == "Completed":

                    self.message_user(
                        request,
                        f"Booking #{booking.id} cannot be cancelled "
                        f"because the rental has already been completed.",
                        level=messages.WARNING,
                    )

                elif booking.status == "Cancelled":

                    self.message_user(
                        request,
                        f"Booking #{booking.id} is already cancelled.",
                        level=messages.INFO,
                    )

                continue

            # ==================================================
            # CANCEL BOOKING
            # ==================================================

            booking.status = "Cancelled"

            booking.save()

            cancelled += 1

        # ==================================================
        # SUCCESS MESSAGE
        # ==================================================

        if cancelled:

            self.message_user(
                request,
                f"{cancelled} booking(s) cancelled successfully.",
                level=messages.SUCCESS,
            )

        # ==================================================
        # SKIPPED MESSAGE
        # ==================================================

        if skipped:

            self.message_user(
                request,
                f"{skipped} booking(s) could not be cancelled "
                f"because of their current status.",
                level=messages.WARNING,
            )

    # ======================================================
    # CONFIRM CASH PAYMENTS
    # ======================================================

    @admin.action(description="Confirm selected cash payments")
    def confirm_payments(self, request, queryset):

        confirmed = 0
        skipped = 0

        for booking in queryset:

            # Only Cash payments can be confirmed
            if booking.payment_method != "Cash":
                skipped += 1
                continue

            # Only Pending Cash payments can be confirmed
            if booking.payment_status != "Pending":
                skipped += 1
                continue

            # Confirm payment
            booking.payment_status = "Paid"

            booking.payment_date = timezone.now()

            # Generate cash confirmation reference
            booking.payment_reference = (
                f"CASH-{booking.id}-CONF-"
                f"{uuid.uuid4().hex[:8].upper()}"
            )

            booking.save()

            confirmed += 1

        if confirmed:

            self.message_user(
                request,
                f"{confirmed} cash payment(s) confirmed successfully.",
                level=messages.SUCCESS,
            )

        if skipped:

            self.message_user(
                request,
                f"{skipped} booking(s) skipped. "
                f"Only Pending Cash payments can be confirmed.",
                level=messages.WARNING,
            )

    # ======================================================
    # START RENTALS
    # ======================================================

    @admin.action(description="Start selected rentals")
    def start_rentals(self, request, queryset):

        started = 0
        skipped = 0

        for booking in queryset:

            # Rental must be approved
            if booking.status != "Approved":
                skipped += 1
                continue

            # Payment must be completed
            if booking.payment_status != "Paid":
                skipped += 1
                continue

            # Documents must be verified
            if booking.document_status != "Verified":
                skipped += 1
                continue

            # Vehicle must exist
            if not booking.car:
                skipped += 1
                continue

            # Vehicle cannot be maintenance/inactive
            if booking.car.fleet_status in [
                "Maintenance",
                "Inactive",
            ]:
                skipped += 1
                continue

            # Start rental
            booking.status = "Active"

            booking.pickup_completed = timezone.now()

            booking.save()

            started += 1

        if started:

            self.message_user(
                request,
                f"{started} rental(s) started successfully.",
                level=messages.SUCCESS,
            )

        if skipped:

            self.message_user(
                request,
                f"{skipped} booking(s) skipped. "
                f"Rental requires Approved status, "
                f"verified documents, and Paid payment.",
                level=messages.WARNING,
            )

    # ======================================================
    # COMPLETE RENTALS
    # ======================================================

    @admin.action(description="Complete selected rentals")
    def complete_rentals(self, request, queryset):

        completed = 0
        skipped = 0

        for booking in queryset:

            # Only active rentals can be completed
            if booking.status != "Active":
                skipped += 1
                continue

            # Complete rental
            booking.status = "Completed"

            booking.return_completed = timezone.now()

            booking.save()

            completed += 1

        if completed:

            self.message_user(
                request,
                f"{completed} rental(s) completed successfully.",
                level=messages.SUCCESS,
            )

        if skipped:

            self.message_user(
                request,
                f"{skipped} booking(s) skipped. "
                f"Only Active rentals can be completed.",
                level=messages.WARNING,
            )


# ==========================================================
# CONTACT ADMIN
# ==========================================================

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "email",
        "created_at",
    )

    search_fields = (
        "name",
        "email",
    )

    list_filter = (
        "created_at",
    )