from datetime import datetime
import os
import uuid
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.tokens import default_token_generator
from django.http import FileResponse, Http404
from django.core.exceptions import PermissionDenied
from django.core.exceptions import PermissionDenied, ValidationError
from django.core.mail import send_mail
from django.core.validators import validate_email
from django.db import models, transaction
from django.db.models import Count, Q, Sum
from django.http import FileResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from .forms import FleetVehicleForm


from .helpers import validate_booking_dates
from .models import Booking, Car, Contact


# ============================================================
# RENTAL STATUS HELPER
# ============================================================

def update_rental_statuses():
    """
    Rental lifecycle states (Approved -> Active -> Completed) are controlled
    via explicit staff actions upon vehicle handover and return inspection.
    This helper is preserved for backward compatibility.
    """
    pass


# ============================================================
# PUBLIC PAGES
# ============================================================

def home(request):

    cars = Car.objects.all()

    return render(
        request,
        "core/homepage.html",
        {
            "cars": cars,
        },
    )


def about(request):

    return render(
        request,
        "core/about.html",
    )


def cars(request):

    cars = Car.objects.all()

    return render(
        request,
        "core/cars.html",
        {
            "cars": cars,
        },
    )


def car_details(request, id):

    car = get_object_or_404(
        Car,
        id=id,
    )

    return render(
        request,
        "core/car_details.html",
        {
            "car": car,
        },
    )


# ============================================================
# CONTACT
# ============================================================

def contact(request):

    if request.method == "POST":

        name = request.POST.get(
            "name",
            "",
        ).strip()

        email = request.POST.get(
            "email",
            "",
        ).strip()

        message = request.POST.get(
            "message",
            "",
        ).strip()

        if not name:

            return render(
                request,
                "core/contact.html",
                {
                    "error": "Name is required.",
                },
            )

        if not email:

            return render(
                request,
                "core/contact.html",
                {
                    "error": "Email is required.",
                },
            )

        try:

            validate_email(email)

        except ValidationError:

            return render(
                request,
                "core/contact.html",
                {
                    "error": "Please enter a valid email address.",
                },
            )

        if len(message) < 10:

            return render(
                request,
                "core/contact.html",
                {
                    "error": (
                        "Message must be at least "
                        "10 characters long."
                    ),
                },
            )

        Contact.objects.create(
            name=name,
            email=email,
            message=message,
        )

        messages.success(
            request,
            "Your message has been sent successfully.",
        )

        return redirect("contact")

    return render(
        request,
        "core/contact.html",
    )


# ============================================================
# AUTHENTICATION
# ============================================================

def register(request):

    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":

        username = request.POST.get(
            "username",
            "",
        ).strip()

        email = request.POST.get(
            "email",
            "",
        ).strip()

        password = request.POST.get(
            "password",
            "",
        )

        confirm_password = request.POST.get(
            "confirm_password",
            "",
        )

        # ----------------------------------------------------
        # USERNAME
        # ----------------------------------------------------

        if not username:

            return render(
                request,
                "core/register.html",
                {
                    "error": "Username is required.",
                },
            )

        if len(username) < 3:

            return render(
                request,
                "core/register.html",
                {
                    "error": (
                        "Username must be at least "
                        "3 characters long."
                    ),
                },
            )

        if User.objects.filter(
            username__iexact=username
        ).exists():

            return render(
                request,
                "core/register.html",
                {
                    "error": "Username already exists.",
                },
            )

        # ----------------------------------------------------
        # EMAIL
        # ----------------------------------------------------

        if not email:

            return render(
                request,
                "core/register.html",
                {
                    "error": "Email is required.",
                },
            )

        try:

            validate_email(email)

        except ValidationError:

            return render(
                request,
                "core/register.html",
                {
                    "error": "Please enter a valid email address.",
                },
            )

        if User.objects.filter(
            email__iexact=email
        ).exists():

            return render(
                request,
                "core/register.html",
                {
                    "error": "Email is already registered.",
                },
            )

        # ----------------------------------------------------
        # PASSWORD CONFIRMATION
        # ----------------------------------------------------

        if not password:

            return render(
                request,
                "core/register.html",
                {
                    "error": "Password is required.",
                },
            )

        if password != confirm_password:

            return render(
                request,
                "core/register.html",
                {
                    "error": "Passwords do not match.",
                },
            )

        # ----------------------------------------------------
        # DJANGO PASSWORD VALIDATION
        # ----------------------------------------------------

        try:

            validate_password(
                password,
                user=User(
                    username=username,
                    email=email,
                ),
            )

        except ValidationError as error:

            return render(
                request,
                "core/register.html",
                {
                    "error": error.messages[0],
                },
            )

        # ----------------------------------------------------
        # CREATE USER
        # ----------------------------------------------------

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
        )

        login(
            request,
            user,
        )

        messages.success(
            request,
            "Your account has been created successfully.",
        )

        return redirect("home")

    return render(
        request,
        "core/register.html",
    )


def user_login(request):

    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":

        username = request.POST.get(
            "username",
            "",
        ).strip()

        password = request.POST.get(
            "password",
            "",
        )

        if not username or not password:

            return render(
                request,
                "core/login.html",
                {
                    "error": (
                        "Username and password "
                        "are required."
                    ),
                },
            )

        user = authenticate(
            request,
            username=username,
            password=password,
        )

        if user is not None:

            login(
                request,
                user,
            )

            if user.is_staff:

                return redirect(
                    "admin_dashboard"
                )

            return redirect(
                "customer_dashboard"
            )

        return render(
            request,
            "core/login.html",
            {
                "error": "Invalid username or password.",
            },
        )

    return render(
        request,
        "core/login.html",
    )


def user_logout(request):

    logout(request)

    return redirect("home")


# ============================================================
# PASSWORD RESET
# ============================================================

def password_reset_request(request):

    """
    Step 1:
    Customer enters email address.

    The response does not reveal whether
    an account exists.
    """

    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":

        email = request.POST.get(
            "email",
            "",
        ).strip()

        if not email:

            return render(
                request,
                "core/password_reset.html",
                {
                    "page": "request",
                    "error": (
                        "Please enter your "
                        "email address."
                    ),
                },
            )

        try:

            validate_email(email)

        except ValidationError:

            return render(
                request,
                "core/password_reset.html",
                {
                    "page": "request",
                    "error": (
                        "Please enter a valid "
                        "email address."
                    ),
                },
            )

        users = User.objects.filter(
            email__iexact=email,
            is_active=True,
        )

        for user in users:

            uid = urlsafe_base64_encode(
                force_bytes(user.pk)
            )

            token = default_token_generator.make_token(
                user
            )

            reset_link = request.build_absolute_uri(
                f"/password-reset-confirm/"
                f"{uid}/{token}/"
            )

            subject = (
                "Smart Car Rental - Password Reset"
            )

            message = f"""
Hello {user.username},

We received a request to reset your
Smart Car Rental account password.

Click the link below to create a new password:

{reset_link}

For your security, this link can only be used once.

If you did not request a password reset,
you can safely ignore this email.

Smart Car Rental
"""

            try:

                send_mail(
                    subject,
                    message,
                    None,
                    [user.email],
                    fail_silently=False,
                )

            except Exception:

                return render(
                    request,
                    "core/password_reset.html",
                    {
                        "page": "request",
                        "error": (
                            "We could not send the "
                            "reset email. Please check "
                            "your email configuration."
                        ),
                    },
                )

        return render(
            request,
            "core/password_reset.html",
            {
                "page": "sent",
                "email": email,
            },
        )

    return render(
        request,
        "core/password_reset.html",
        {
            "page": "request",
        },
    )


def password_reset_confirm(
    request,
    uidb64,
    token,
):

    if request.user.is_authenticated:
        return redirect("home")

    try:

        uid = force_str(
            urlsafe_base64_decode(uidb64)
        )

        user = User.objects.get(
            pk=uid
        )

    except (
        TypeError,
        ValueError,
        OverflowError,
        User.DoesNotExist,
    ):

        user = None

    if (
        user is None
        or not default_token_generator.check_token(
            user,
            token,
        )
    ):

        return render(
            request,
            "core/password_reset.html",
            {
                "page": "invalid",
            },
        )

    form = SetPasswordForm(
        user=user,
        data=request.POST or None,
    )

    if request.method == "POST":

        if form.is_valid():

            form.save()

            return redirect(
                "password_reset_complete"
            )

    return render(
        request,
        "core/password_reset.html",
        {
            "page": "confirm",
            "form": form,
        },
    )


def password_reset_complete(request):

    if request.user.is_authenticated:
        return redirect("home")

    return render(
        request,
        "core/password_reset.html",
        {
            "page": "complete",
        },
    )


# ============================================================
# CUSTOMER BOOKING
# ============================================================

@login_required
def booking(request):

    cars = Car.objects.all()

    # ========================================================
    # POST
    # ========================================================

    if request.method == "POST":

        selected_car = get_object_or_404(
            Car,
            name=request.POST.get("car_type"),
        )

        # ----------------------------------------------------
        # DATE VALIDATION
        # ----------------------------------------------------

        try:

            pickup, dropoff = validate_booking_dates(
                request
            )

        except ValueError as error:

            return render(
                request,
                "core/booking.html",
                {
                    "cars": cars,
                    "selected_car": selected_car.name,
                    "error": str(error),
                },
            )

        # ----------------------------------------------------
        # DATE-SPECIFIC AVAILABILITY
        # ----------------------------------------------------

        available_for_dates = (
            selected_car.available_for_dates(
                pickup,
                dropoff,
            )
        )

        if available_for_dates <= 0:

            return render(
                request,
                "core/booking.html",
                {
                    "cars": cars,
                    "selected_car": selected_car.name,
                    "error": (
                        "Sorry! This car is currently "
                        "unavailable for the selected dates."
                    ),
                },
            )

        # ----------------------------------------------------
        # CUSTOMER INFORMATION
        # ----------------------------------------------------

        first_name = request.POST.get(
            "first_name",
            "",
        ).strip()

        middle_name = request.POST.get(
            "middle_name",
            "",
        ).strip()

        last_name = request.POST.get(
            "last_name",
            "",
        ).strip()

        email = request.POST.get(
            "email",
            "",
        ).strip()

        phone = request.POST.get(
            "phone",
            "",
        ).strip()

        pickup_location = request.POST.get(
            "pickup_location",
            "",
        ).strip()

        if not first_name:

            return render(
                request,
                "core/booking.html",
                {
                    "cars": cars,
                    "selected_car": selected_car.name,
                    "error": "First name is required.",
                },
            )

        if not last_name:

            return render(
                request,
                "core/booking.html",
                {
                    "cars": cars,
                    "selected_car": selected_car.name,
                    "error": "Last name is required.",
                },
            )

        if not email:

            return render(
                request,
                "core/booking.html",
                {
                    "cars": cars,
                    "selected_car": selected_car.name,
                    "error": "Email is required.",
                },
            )

        try:

            validate_email(email)

        except ValidationError:

            return render(
                request,
                "core/booking.html",
                {
                    "cars": cars,
                    "selected_car": selected_car.name,
                    "error": "Invalid email address.",
                },
            )

        if not pickup_location:

            return render(
                request,
                "core/booking.html",
                {
                    "cars": cars,
                    "selected_car": selected_car.name,
                    "error": (
                        "Pickup location is required."
                    ),
                },
            )

        # ----------------------------------------------------
        # DOCUMENT UPLOAD
        # ----------------------------------------------------

        driver_license = request.FILES.get(
            "driver_license"
        )

        national_id = request.FILES.get(
            "national_id"
        )

        if not driver_license:

            return render(
                request,
                "core/booking.html",
                {
                    "cars": cars,
                    "selected_car": selected_car.name,
                    "error": (
                        "Driver license is required."
                    ),
                },
            )

        if not national_id:

            return render(
                request,
                "core/booking.html",
                {
                    "cars": cars,
                    "selected_car": selected_car.name,
                    "error": (
                        "National ID is required."
                    ),
                },
            )

        # ----------------------------------------------------
        # FILE VALIDATION
        # ----------------------------------------------------

        allowed_extensions = {
            ".pdf",
            ".jpg",
            ".jpeg",
            ".png",
        }

        driver_ext = os.path.splitext(
            driver_license.name
        )[1].lower()

        id_ext = os.path.splitext(
            national_id.name
        )[1].lower()

        if driver_ext not in allowed_extensions:

            return render(
                request,
                "core/booking.html",
                {
                    "cars": cars,
                    "selected_car": selected_car.name,
                    "error": (
                        "Driver license must be PDF, JPG, "
                        "JPEG or PNG."
                    ),
                },
            )

        if id_ext not in allowed_extensions:

            return render(
                request,
                "core/booking.html",
                {
                    "cars": cars,
                    "selected_car": selected_car.name,
                    "error": (
                        "National ID must be PDF, JPG, "
                        "JPEG or PNG."
                    ),
                },
            )

        # ----------------------------------------------------
        # CREATE BOOKING
        # ----------------------------------------------------

        try:

            Booking.objects.create(
                user=request.user,
                car=selected_car,
                car_type=selected_car.name,
                status="Pending",
                pickup_date=pickup,
                dropoff_date=dropoff,
                pickup_location=pickup_location,
                first_name=first_name,
                middle_name=middle_name,
                last_name=last_name,
                email=email,
                phone=phone,
                driver_license=driver_license,
                national_id=national_id,
            )

        except ValidationError as error:

            return render(
                request,
                "core/booking.html",
                {
                    "cars": cars,
                    "selected_car": selected_car.name,
                    "error": error.messages[0],
                },
            )

        messages.success(
            request,
            "Your booking has been submitted successfully.",
        )

        return redirect(
            "my_bookings"
        )

    # ========================================================
    # GET
    # ========================================================

    selected_car = request.GET.get(
        "car"
    )

    error = None

    if selected_car:

        car = get_object_or_404(
            Car,
            name=selected_car,
        )

        if car.available_quantity <= 0:

            error = (
                "Sorry! This car is currently unavailable."
            )

    return render(
        request,
        "core/booking.html",
        {
            "cars": cars,
            "selected_car": selected_car,
            "error": error,
        },
    )


# ============================================================
# CUSTOMER BOOKINGS
# ============================================================

@login_required
def my_bookings(request):

    bookings = (
        Booking.objects
        .select_related("car")
        .filter(user=request.user)
        .order_by("-pickup_date", "-created_at")
    )

    return render(
        request,
        "core/my_bookings.html",
        {
            "bookings": bookings,
        },
    )


@login_required
def booking_detail(request, booking_id=None, id=None):
    """
    Unified booking detail workspace for both customers and staff.
    - Staff can access and inspect any booking.
    - Customers can only access their own bookings.
    """
    actual_id = booking_id if booking_id is not None else id

    if request.user.is_staff:
        booking = get_object_or_404(
            Booking.objects.select_related("car", "user"),
            id=actual_id,
        )
    else:
        booking = get_object_or_404(
            Booking.objects.select_related("car", "user"),
            id=actual_id,
            user=request.user,
        )

    context = {
        "booking": booking,
        "customer_name": " ".join(
            part
            for part in [
                booking.first_name,
                booking.middle_name,
                booking.last_name,
            ]
            if part
        ),
        "vehicle": booking.car,
        "rental_days": booking.rental_days,
        "documents_complete": bool(
            booking.driver_license and booking.national_id
        ),
        "can_approve": (
            booking.status == "Pending"
            and booking.document_status == "Verified"
            and booking.car is not None
        ),
        "can_start_rental": (
            booking.status == "Approved"
            and booking.payment_status == "Paid"
            and booking.document_status == "Verified"
        ),
        "can_complete_rental": (
            booking.status == "Active"
        ),
    }

    return render(
        request,
        "core/booking_detail.html",
        context,
    )


@login_required
@require_POST
def cancel_booking(request, booking_id):
    """
    Cancel an existing booking. Protected with POST and CSRF.
    """
    if request.user.is_staff:
        booking = get_object_or_404(Booking, id=booking_id)
    else:
        booking = get_object_or_404(Booking, id=booking_id, user=request.user)

    if booking.status not in ["Pending", "Approved"]:
        messages.error(
            request,
            "This booking can no longer be cancelled."
        )
        if request.user.is_staff:
            return redirect("booking_management")
        return redirect("customer_dashboard")

    booking.status = "Cancelled"
    booking.save(update_fields=["status"])

    messages.success(
        request,
        f"Booking #{booking.id} has been cancelled."
    )

    if request.user.is_staff:
        return redirect("booking_management")
    return redirect("customer_dashboard")


# ============================================================
# BOOKING DOCUMENTS
# ============================================================

@login_required
def booking_document(request, booking_id, document_type):

    booking = get_object_or_404(
        Booking,
        id=booking_id,
    )

    # --------------------------------------------------------
    # ACCESS CONTROL
    # --------------------------------------------------------

    if not request.user.is_staff and booking.user != request.user:
        raise PermissionDenied(
            "You are not allowed to access this document."
        )

    # --------------------------------------------------------
    # SELECT DOCUMENT
    # --------------------------------------------------------

    if document_type == "license":
        document = booking.driver_license

    elif document_type == "national-id":
        document = booking.national_id

    else:
        raise PermissionDenied(
            "Invalid document type."
        )

    # --------------------------------------------------------
    # DOCUMENT EXISTS IN DATABASE?
    # --------------------------------------------------------

    if not document:
        raise Http404(
            "Requested document does not exist."
        )

    # --------------------------------------------------------
    # DOCUMENT EXISTS ON DISK?
    # --------------------------------------------------------

    try:
        document.open("rb")

    except (FileNotFoundError, OSError):
        raise Http404(
            "The requested document file is unavailable."
        )

    # --------------------------------------------------------
    # RETURN DOCUMENT
    # --------------------------------------------------------

    return FileResponse(
        document,
        as_attachment=False,
        filename=os.path.basename(document.name),
    )

# ============================================================
# CUSTOMER PAYMENT
# ============================================================

@login_required
def payment(
    request,
    id,
):

    booking = get_object_or_404(
        Booking,
        id=id,
        user=request.user,
    )

    # --------------------------------------------------------
    # INVALID BOOKING STATE
    # --------------------------------------------------------

    if booking.status in [
        "Cancelled",
        "Rejected",
        "Completed",
    ]:

        messages.error(
            request,
            "This booking cannot be paid.",
        )

        return redirect(
            "booking_detail",
            booking_id=booking.id,
        )

    # --------------------------------------------------------
    # PAYMENT ONLY AFTER APPROVAL
    # --------------------------------------------------------

    if booking.status != "Approved":

        messages.error(
            request,
            (
                "Payment is available only "
                "after your booking has been approved."
            ),
        )

        return redirect(
            "booking_detail",
            id=booking.id,
        )

    # --------------------------------------------------------
    # ALREADY PAID
    # --------------------------------------------------------

    if booking.payment_status == "Paid":

        messages.info(
            request,
            "This booking has already been paid.",
        )

        return redirect(
            "payment_receipt",
            id=booking.id,
        )

    # --------------------------------------------------------
    # POST
    # --------------------------------------------------------

    if request.method == "POST":

        payment_method = request.POST.get(
            "payment_method",
            "",
        ).strip()

        allowed_methods = {
            "Chapa",
            "Telebirr",
            "Cash",
        }

        if payment_method not in allowed_methods:

            messages.error(
                request,
                "Please select a valid payment method.",
            )

            return render(
                request,
                "core/payment.html",
                {
                    "booking": booking,
                },
            )

        # ----------------------------------------------------
        # CASH PAYMENT
        # ----------------------------------------------------

        if payment_method == "Cash":

            booking.payment_method = "Cash"
            booking.payment_status = "Pending"

            booking.payment_reference = (
                f"CASH-{booking.id}-"
                f"{uuid.uuid4().hex[:10].upper()}"
            )

            booking.payment_date = None

            try:

                booking.save()

            except ValidationError as error:

                messages.error(
                    request,
                    (
                        "Payment could not be recorded: "
                        f"{error}"
                    ),
                )

                return render(
                    request,
                    "core/payment.html",
                    {
                        "booking": booking,
                    },
                )

            return render(
                request,
                "core/payment.html",
                {
                    "booking": booking,
                    "cash_payment_pending": True,
                },
            )

        # ----------------------------------------------------
        # ONLINE PAYMENT
        # ----------------------------------------------------
        #
        # NOTE:
        # This remains a development/simulation flow.
        # Production Chapa/Telebirr must use provider APIs
        # and server-side callback/webhook verification.
        # ----------------------------------------------------

        booking.payment_method = payment_method
        booking.payment_status = "Paid"

        booking.payment_reference = (
            f"SIM-{booking.id}-"
            f"{uuid.uuid4().hex[:10].upper()}"
        )

        booking.payment_date = timezone.now()

        try:

            booking.save()

        except ValidationError as error:

            messages.error(
                request,
                (
                    "Payment could not be recorded: "
                    f"{error}"
                ),
            )

            return render(
                request,
                "core/payment.html",
                {
                    "booking": booking,
                },
            )

        messages.success(
            request,
            (
                f"{payment_method} payment "
                "completed successfully."
            ),
        )

        return redirect(
            "payment_receipt",
            id=booking.id,
        )

    return render(
        request,
        "core/payment.html",
        {
            "booking": booking,
        },
    )


@login_required
def payment_receipt(
    request,
    id,
):

    booking = get_object_or_404(
        Booking,
        id=id,
        user=request.user,
    )

    if booking.payment_status == "Paid":

        return render(
            request,
            "core/payment_receipt.html",
            {
                "booking": booking,
            },
        )

    if (
        booking.payment_status == "Pending"
        and booking.payment_method == "Cash"
    ):

        return render(
            request,
            "core/payment_receipt.html",
            {
                "booking": booking,
            },
        )

    return redirect(
        "payment_history"
    )


@login_required
def payment_history(request):

    payments = (
        Booking.objects
        .filter(user=request.user)
        .order_by("-created_at")
    )

    return render(
        request,
        "core/payment_history.html",
        {
            "payments": payments,
        },
    )


# ============================================================
# CUSTOMER DASHBOARD
# ============================================================

@login_required
def customer_dashboard(request):

    bookings = (
        Booking.objects
        .filter(user=request.user)
        .select_related("car")
        .order_by("-created_at")
    )

    active_rentals = bookings.filter(
        status="Active"
    ).count()

    upcoming_bookings = bookings.filter(
        status="Approved"
    ).count()

    completed_rentals = bookings.filter(
        status="Completed"
    ).count()

    cancelled_bookings = bookings.filter(
        status="Cancelled"
    ).count()

    active_bookings = bookings.filter(
        status="Active"
    )

    upcoming_bookings_list = bookings.filter(
        status="Approved"
    )

    rental_history = bookings.filter(
        status__in=[
            "Completed",
            "Cancelled",
            "Rejected",
        ]
    )

    context = {
        "bookings": bookings,
        "active_rentals": active_rentals,
        "upcoming_bookings": upcoming_bookings,
        "completed_rentals": completed_rentals,
        "cancelled_bookings": cancelled_bookings,
        "active_bookings": active_bookings,
        "upcoming_bookings_list": upcoming_bookings_list,
        "rental_history": rental_history,
        "user": request.user,
    }

    return render(
        request,
        "core/customer_dashboard.html",
        context,
    )


# ============================================================
# CUSTOMER PROFILE
# ============================================================

@login_required
def profile(request):

    bookings = Booking.objects.filter(
        user=request.user
    )

    context = {
        "total_bookings": bookings.count(),
        "pending_bookings": bookings.filter(
            status="Pending"
        ).count(),
        "approved_bookings": bookings.filter(
            status="Approved"
        ).count(),
        "active_bookings": bookings.filter(
            status="Active"
        ).count(),
        "completed_bookings": bookings.filter(
            status="Completed"
        ).count(),
        "cancelled_bookings": bookings.filter(
            status="Cancelled"
        ).count(),
    }

    return render(
        request,
        "core/profile.html",
        context,
    )


# ============================================================
# NOTIFICATIONS
# ============================================================

@login_required
def notifications(request):

    user_bookings = (
        Booking.objects
        .filter(user=request.user)
        .select_related("car")
        .order_by("-created_at")
    )

    notification_list = []

    for booking in user_bookings:

        if booking.status == "Pending":

            notification_list.append({
                "title": "Booking Submitted",
                "message": (
                    f"Your booking for "
                    f"{booking.car.name} is waiting "
                    f"for approval."
                ),
                "type": "info",
                "date": booking.created_at,
            })

        elif booking.status == "Approved":

            notification_list.append({
                "title": "Booking Approved",
                "message": (
                    f"Your booking for "
                    f"{booking.car.name} has been approved."
                ),
                "type": "success",
                "date": booking.created_at,
            })

        elif booking.status == "Active":

            notification_list.append({
                "title": "Rental Started",
                "message": (
                    f"You have picked up "
                    f"your {booking.car.name}."
                ),
                "type": "success",
                "date": booking.pickup_completed,
            })

        elif booking.status == "Completed":

            notification_list.append({
                "title": "Rental Completed",
                "message": (
                    f"Thank you for returning "
                    f"{booking.car.name}."
                ),
                "type": "success",
                "date": booking.return_completed,
            })

        elif booking.status == "Cancelled":

            notification_list.append({
                "title": "Booking Cancelled",
                "message": (
                    f"Your booking for "
                    f"{booking.car.name} has been cancelled."
                ),
                "type": "warning",
                "date": booking.created_at,
            })

        elif booking.status == "Rejected":

            notification_list.append({
                "title": "Booking Rejected",
                "message": (
                    f"Your booking for "
                    f"{booking.car.name} was rejected."
                ),
                "type": "danger",
                "date": booking.created_at,
            })

    return render(
        request,
        "core/notifications.html",
        {
            "notifications": notification_list,
        },
    )


# ============================================================
# ACCOUNT SETTINGS
# ============================================================

@login_required
def account_settings(request):

    if request.method == "POST":

        first_name = request.POST.get(
            "first_name",
            "",
        ).strip()

        last_name = request.POST.get(
            "last_name",
            "",
        ).strip()

        email = request.POST.get(
            "email",
            "",
        ).strip()

        if not email:

            return render(
                request,
                "core/account_settings.html",
                {
                    "error": "Email is required.",
                },
            )

        try:

            validate_email(email)

        except ValidationError:

            return render(
                request,
                "core/account_settings.html",
                {
                    "error": (
                        "Please enter a valid "
                        "email address."
                    ),
                },
            )

        if (
            User.objects
            .exclude(id=request.user.id)
            .filter(email__iexact=email)
            .exists()
        ):

            return render(
                request,
                "core/account_settings.html",
                {
                    "error": (
                        "That email is already being "
                        "used by another account."
                    ),
                },
            )

        request.user.first_name = first_name
        request.user.last_name = last_name
        request.user.email = email

        request.user.save(
            update_fields=[
                "first_name",
                "last_name",
                "email",
            ]
        )

        messages.success(
            request,
            (
                "Your account has been "
                "updated successfully."
            ),
        )

        return redirect(
            "account_settings"
        )

    return render(
        request,
        "core/account_settings.html",
    )


# ============================================================
# ADMIN PROFILE
# ============================================================

@staff_member_required
def admin_profile(request):

    if request.method == "POST":

        user = request.user

        first_name = request.POST.get(
            "first_name",
            "",
        ).strip()

        last_name = request.POST.get(
            "last_name",
            "",
        ).strip()

        email = request.POST.get(
            "email",
            "",
        ).strip()

        if not email:

            return render(
                request,
                "core/admin_profile.html",
                {
                    "error": "Email is required.",
                },
            )

        try:

            validate_email(email)

        except ValidationError:

            return render(
                request,
                "core/admin_profile.html",
                {
                    "error": (
                        "Please enter a valid "
                        "email address."
                    ),
                },
            )

        if (
            User.objects
            .exclude(id=user.id)
            .filter(email__iexact=email)
            .exists()
        ):

            return render(
                request,
                "core/admin_profile.html",
                {
                    "error": (
                        "That email is already "
                        "being used."
                    ),
                },
            )

        user.first_name = first_name
        user.last_name = last_name
        user.email = email

        user.save(
            update_fields=[
                "first_name",
                "last_name",
                "email",
            ]
        )

        messages.success(
            request,
            "Your profile has been updated successfully.",
        )

        return redirect(
            "admin_profile"
        )

    return render(
        request,
        "core/admin_profile.html",
    )


# ============================================================
# ADMIN DASHBOARD
# ============================================================

@staff_member_required
def admin_dashboard(request):
    """
    Professional admin dashboard.

    All dashboard statistics are calculated inside this function
    so they are available to the template.
    """

    # ============================================================
    # KEEP RENTAL STATUSES CURRENT
    # ============================================================

    update_rental_statuses()

    today = timezone.localdate()

    # ============================================================
    # BASE QUERYSETS
    # ============================================================

    cars = Car.objects.all()
    bookings = Booking.objects.select_related(
        "user",
        "car",
    )

    # ============================================================
    # BOOKING STATISTICS
    # ============================================================

    total_bookings = bookings.count()

    pending_bookings = bookings.filter(
        status="Pending"
    ).count()

    approved_bookings = bookings.filter(
        status="Approved"
    ).count()

    active_rentals = bookings.filter(
        status="Active"
    ).count()

    completed_bookings = bookings.filter(
        status="Completed"
    ).count()

    cancelled_bookings = bookings.filter(
        status="Cancelled"
    ).count()

    rejected_bookings = bookings.filter(
        status="Rejected"
    ).count()

    # ============================================================
    # FLEET STATISTICS
    # ============================================================

    total_cars = cars.count()

    available_cars = cars.filter(
        fleet_status="Available"
    ).count()

    maintenance_cars = cars.filter(
        fleet_status="Maintenance"
    ).count()

    inactive_cars = cars.filter(
        fleet_status="Inactive"
    ).count()

    total_fleet_units = sum(
        car.total_quantity or 0
        for car in cars
    )

    available_fleet_units = sum(
        car.available_quantity or 0
        for car in cars
    )

    maintenance_fleet_units = sum(
        car.maintenance_count or 0
        for car in cars
    )

    rented_fleet_units = sum(
        max(
            (car.total_quantity or 0)
            - (car.available_quantity or 0)
            - (car.maintenance_count or 0),
            0,
        )
        for car in cars
    )

    inactive_fleet_units = sum(
        (car.total_quantity or 0)
        for car in cars.filter(
            fleet_status="Inactive"
        )
    )

    # ============================================================
    # FLEET UTILIZATION
    # ============================================================

    if total_fleet_units > 0:
        fleet_utilization = round(
            (
                rented_fleet_units
                / total_fleet_units
            ) * 100,
            1,
        )
    else:
        fleet_utilization = 0

    # ============================================================
    # TODAY'S OPERATIONS
    # ============================================================

    today_pickups = bookings.filter(
        pickup_date=today,
        status__in=[
            "Approved",
            "Active",
        ],
    ).count()

    today_returns = bookings.filter(
        dropoff_date=today,
        status="Active",
    ).count()

    overdue_rentals = bookings.filter(
        status="Active",
        dropoff_date__lt=today,
    ).count()

    completed_pickups_today = bookings.filter(
        pickup_completed__date=today
    ).count()

    completed_returns_today = bookings.filter(
        return_completed__date=today
    ).count()

    today_pickup_list = bookings.filter(
        pickup_date=today,
        status__in=[
            "Approved",
            "Active",
        ],
    ).select_related(
        "user",
        "car",
    ).order_by(
        "pickup_date",
        "id",
    )

    today_return_list = bookings.filter(
        dropoff_date=today,
        status="Active",
    ).select_related(
        "user",
        "car",
    ).order_by(
        "dropoff_date",
        "id",
    )

    overdue_rental_list = bookings.filter(
        status="Active",
        dropoff_date__lt=today,
    ).select_related(
        "user",
        "car",
    ).order_by(
        "dropoff_date",
    )

    # ============================================================
    # DOCUMENT STATISTICS
    # ============================================================

    pending_documents = bookings.filter(
        document_status="Pending"
    ).count()

    verified_documents = bookings.filter(
        document_status="Verified"
    ).count()

    rejected_documents = bookings.filter(
        document_status="Rejected"
    ).count()

    pending_document_list = bookings.filter(
        document_status="Pending"
    ).select_related(
        "user",
        "car",
    ).order_by(
        "-created_at"
    )[:10]

    # ============================================================
    # CUSTOMER / STAFF STATISTICS
    # ============================================================

    total_customers = User.objects.filter(
        is_staff=False,
        is_superuser=False,
    ).count()

    staff_users = User.objects.filter(
        is_staff=True
    ).count()

    # ============================================================
    # REVENUE / PAYMENT STATISTICS
    # ============================================================

    paid_revenue = bookings.filter(
        payment_status="Paid"
    ).aggregate(
        total=Sum("total_price")
    )["total"] or 0

    total_revenue = bookings.filter(
        status="Completed",
        payment_status="Paid",
    ).aggregate(
        total=Sum("total_price")
    )["total"] or 0

    pending_payment_count = bookings.filter(
        payment_status="Pending"
    ).count()

    paid_payment_count = bookings.filter(
        payment_status="Paid"
    ).count()

    failed_payment_count = bookings.filter(
        payment_status="Failed"
    ).count()

    refunded_payment_count = bookings.filter(
        payment_status="Refunded"
    ).count()

    pending_payment_list = bookings.filter(
        payment_status="Pending"
    ).select_related(
        "user",
        "car",
    ).order_by(
        "-created_at"
    )[:10]

    # ============================================================
    # MOST POPULAR CAR
    # ============================================================

    popular_car = cars.annotate(
        booking_count=Count("booking")
    ).order_by(
        "-booking_count"
    ).first()

    # ============================================================
    # RECENT BOOKINGS
    # ============================================================

    recent_bookings = bookings.order_by(
        "-created_at"
    )[:10]

    pending_booking_list = bookings.filter(
        status="Pending"
    ).select_related(
        "user",
        "car",
    ).order_by(
        "-created_at"
    )[:10]

    # ============================================================
    # DASHBOARD CONTEXT
    # ============================================================

    context = {
        # Fleet
        "cars": cars,
        "total_cars": total_cars,
        "available_cars": available_cars,
        "maintenance_cars": maintenance_cars,
        "inactive_cars": inactive_cars,

        "total_fleet_units": total_fleet_units,
        "available_fleet_units": available_fleet_units,
        "rented_fleet_units": rented_fleet_units,
        "maintenance_fleet_units": maintenance_fleet_units,
        "inactive_fleet_units": inactive_fleet_units,
        "fleet_utilization": fleet_utilization,

        # Bookings
        "total_bookings": total_bookings,
        "pending_bookings": pending_bookings,
        "approved_bookings": approved_bookings,
        "active_rentals": active_rentals,
        "completed_bookings": completed_bookings,
        "cancelled_bookings": cancelled_bookings,
        "rejected_bookings": rejected_bookings,

        # Operations
        "today": today,
        "today_pickups": today_pickups,
        "today_returns": today_returns,
        "overdue_rentals": overdue_rentals,
        "completed_pickups_today": completed_pickups_today,
        "completed_returns_today": completed_returns_today,

        "today_pickup_list": today_pickup_list,
        "today_return_list": today_return_list,
        "overdue_rental_list": overdue_rental_list,

        # Documents
        "pending_documents": pending_documents,
        "verified_documents": verified_documents,
        "rejected_documents": rejected_documents,
        "pending_document_list": pending_document_list,

        # Users
        "total_customers": total_customers,
        "staff_users": staff_users,

        # Payments
        "paid_revenue": paid_revenue,
        "total_revenue": total_revenue,
        "pending_payment_count": pending_payment_count,
        "paid_payment_count": paid_payment_count,
        "failed_payment_count": failed_payment_count,
        "refunded_payment_count": refunded_payment_count,
        "pending_payment_list": pending_payment_list,

        # Analytics
        "popular_car": popular_car,

        # Recent activity
        "recent_bookings": recent_bookings,
        "pending_booking_list": pending_booking_list,
    }

    # ============================================================
    # RENDER
    # ============================================================

    return render(
        request,
        "core/admin_dashboard.html",
        context,
    )
# ============================================================
# CUSTOMER MANAGEMENT
# ============================================================

@staff_member_required

def customer_management(request):

    search = request.GET.get("search", "").strip()

    customers = (
        User.objects
        .filter(
            is_staff=False,
            is_superuser=False
        )
        .annotate(
            total_bookings=Count(
                "booking",
                distinct=True
            ),

            active_bookings=Count(
                "booking",
                filter=Q(
                    booking__status="Active"
                ),
                distinct=True,
            ),

            completed_bookings=Count(
                "booking",
                filter=Q(
                    booking__status="Completed"
                ),
                distinct=True,
            ),

            total_spent=Sum(
                "booking__total_price",
                filter=Q(
                    booking__payment_status="Paid"
                ),
            ),
        )
        .order_by("-date_joined")
    )


    # ========================================================
    # SEARCH
    # ========================================================

    if search:

        customers = customers.filter(
            Q(username__icontains=search)
            |
            Q(first_name__icontains=search)
            |
            Q(last_name__icontains=search)
            |
            Q(email__icontains=search)
        )


    # ========================================================
    # SUMMARY STATISTICS
    # ========================================================

    all_customers = User.objects.filter(
        is_staff=False,
        is_superuser=False
        )

    total_customers = all_customers.count()

    active_customers = all_customers.filter(
        is_active=True
    ).count()

    inactive_customers = all_customers.filter(

    ).count()

    customers_with_rentals = all_customers.filter(
        booking__isnull=False
    ).distinct().count()


    context = {

        "customers": customers,

        "search": search,

        "total_customers": total_customers,

        "active_customers": active_customers,

        "inactive_customers": inactive_customers,

        "customers_with_rentals": customers_with_rentals,

    }


    return render(
        request,
        "core/customer_management.html",
        context
    )

# ============================================================
# CUSTOMER DETAIL
# ============================================================
@staff_member_required
def customer_detail(request, user_id):

    # --------------------------------------------------------
    # Get customer
    # --------------------------------------------------------

    customer = get_object_or_404(
        User,
        id=user_id,
        is_staff=False,
        is_superuser=False,
    )

    # --------------------------------------------------------
    # Customer bookings
    #
    # Your existing project uses the reverse relationship:
    # customer.booking
    # --------------------------------------------------------

    bookings = (
        customer.booking
        .select_related("car")
        .order_by("-id")
    )

    # --------------------------------------------------------
    # Booking statistics
    # --------------------------------------------------------

    total_bookings = bookings.count()

    active_bookings = bookings.filter(
        status="Active"
    ).count()

    completed_bookings = bookings.filter(
        status="Completed"
    ).count()

    pending_bookings = bookings.filter(
        status="Pending"
    ).count()

    cancelled_bookings = bookings.filter(
        status="Cancelled"
    ).count()

    # --------------------------------------------------------
    # Total paid amount
    # --------------------------------------------------------

    total_spent = (
        bookings
        .filter(payment_status="Paid")
        .aggregate(
            total=Sum("total_price")
        )
        ["total"]
    )

    if total_spent is None:
        total_spent = 0

    # --------------------------------------------------------
    # Last booking
    # --------------------------------------------------------

    last_booking = bookings.first()

    # --------------------------------------------------------
    # Current rental
    # --------------------------------------------------------

    current_rental = (
        bookings
        .filter(status="Active")
        .first()
    )

    # --------------------------------------------------------
    # Payment statistics
    # --------------------------------------------------------

    paid_bookings = bookings.filter(
        payment_status="Paid"
    ).count()

    unpaid_bookings = bookings.exclude(
        payment_status="Paid"
    ).count()

    # --------------------------------------------------------
    # Customer context
    # --------------------------------------------------------

    context = {
        "customer": customer,
        "bookings": bookings,

        "total_bookings": total_bookings,
        "active_bookings": active_bookings,
        "completed_bookings": completed_bookings,
        "pending_bookings": pending_bookings,
        "cancelled_bookings": cancelled_bookings,

        "total_spent": total_spent,

        "last_booking": last_booking,
        "current_rental": current_rental,

        "paid_bookings": paid_bookings,
        "unpaid_bookings": unpaid_bookings,
    }

    return render(
        request,
        "core/customer_detail.html",
        context
    )
# ============================================================
# FLEET MANAGEMENT
# ============================================================

@staff_member_required
def fleet_management(request):

    cars = Car.objects.all().order_by("name")

    # --------------------------------------------------------
    # SEARCH
    # --------------------------------------------------------

    search = request.GET.get(
        "search",
        "",
    ).strip()

    if search:
        cars = cars.filter(
            Q(name__icontains=search)
            | Q(plate_number__icontains=search)
            | Q(model_year__icontains=search)
        )

    # --------------------------------------------------------
    # STATUS FILTER
    # --------------------------------------------------------

    status = request.GET.get(
        "status",
        "All",
    )

    valid_fleet_statuses = {
        "Available",
        "Maintenance",
        "Inactive",
    }

    # "Reserved" and "Rented" are booking states,
    # not Car.fleet_status values.
    if status == "Reserved":
        cars = cars.filter(
            booking__status="Approved"
        ).distinct()

    elif status == "Rented":
        cars = cars.filter(
            booking__status="Active"
        ).distinct()

    elif (
        status
        and status != "All"
        and status in valid_fleet_statuses
    ):
        cars = cars.filter(
            fleet_status=status
        )

    # --------------------------------------------------------
    # FLEET DATA
    # --------------------------------------------------------

    fleet_data = []

    total_vehicles = 0
    available_vehicles = 0
    reserved_vehicles = 0
    rented_vehicles = 0
    maintenance_vehicles = 0
    inactive_vehicles = 0

    for car in cars:

        total_quantity = max(
            0,
            car.total_quantity or 0,
        )

        # ----------------------------------------------------
        # RESERVED
        # Approved bookings = future/reserved vehicles
        # ----------------------------------------------------

        reserved_count = Booking.objects.filter(
            car=car,
            status="Approved",
        ).count()

        # ----------------------------------------------------
        # RENTED
        # Active bookings = currently rented vehicles
        # ----------------------------------------------------

        rented_count = Booking.objects.filter(
            car=car,
            status="Active",
        ).count()

        # ----------------------------------------------------
        # MAINTENANCE
        # ----------------------------------------------------

        maintenance_count = max(
            0,
            car.maintenance_count or 0,
        )

        if maintenance_count > total_quantity:
            maintenance_count = total_quantity

        # ----------------------------------------------------
        # INACTIVE
        # ----------------------------------------------------

        if car.fleet_status == "Inactive":
            inactive_count = total_quantity
        else:
            inactive_count = 0

        # ----------------------------------------------------
        # AVAILABLE
        #
        # Available units are units not reserved, rented,
        # maintained, or inactive.
        # ----------------------------------------------------

        unavailable_units = (
            reserved_count
            + rented_count
            + maintenance_count
            + inactive_count
        )

        available = max(
            0,
            total_quantity - unavailable_units,
        )

        # ----------------------------------------------------
        # SAFETY CAP
        #
        # Prevent bad historical data from making the counts
        # exceed the fleet size.
        # ----------------------------------------------------

        reserved_count = min(
            reserved_count,
            total_quantity,
        )

        rented_count = min(
            rented_count,
            total_quantity,
        )

        available = min(
            available,
            total_quantity,
        )

        # ----------------------------------------------------
        # TOTALS
        # ----------------------------------------------------

        total_vehicles += total_quantity
        available_vehicles += available
        reserved_vehicles += reserved_count
        rented_vehicles += rented_count
        maintenance_vehicles += maintenance_count
        inactive_vehicles += inactive_count

        # ----------------------------------------------------
        # ROW DATA
        # ----------------------------------------------------

        fleet_data.append({
            "car": car,
            "available": available,
            "reserved_count": reserved_count,
            "rented_count": rented_count,
            "maintenance_count": maintenance_count,
            "inactive_count": inactive_count,
        })

    # --------------------------------------------------------
    # CONTEXT
    # --------------------------------------------------------

    context = {
        "fleet_data": fleet_data,

        "total_vehicles": total_vehicles,
        "available_vehicles": available_vehicles,
        "reserved_vehicles": reserved_vehicles,
        "rented_vehicles": rented_vehicles,
        "maintenance_vehicles": maintenance_vehicles,
        "inactive_vehicles": inactive_vehicles,

        "search": search,
        "status": status,
    }

    return render(
        request,
        "core/fleet_management.html",
        context,
    )


# ============================================================
# FLEET VEHICLE EDIT
# ============================================================

@staff_member_required
def fleet_vehicle_edit(request, car_id):
    """
    Edit an existing fleet vehicle.

    Important:
    - Uses FleetVehicleForm for validation.
    - Prevents total_quantity from being reduced below
      the number of currently Approved/Active bookings.
    - Does not modify booking availability logic.
    - Does not modify existing rental/booking records.
    """

    car = get_object_or_404(
        Car,
        id=car_id,
    )

    if request.method == "POST":

        form = FleetVehicleForm(
            request.POST,
            request.FILES,
            instance=car,
        )

        if form.is_valid():

            total_quantity = form.cleaned_data.get(
                "total_quantity"
            )

            # ------------------------------------------------
            # PROTECT CURRENT RENTALS / RESERVATIONS
            # ------------------------------------------------

            active_or_approved_count = (
                Booking.objects
                .filter(
                    car=car,
                    status__in=[
                        "Approved",
                        "Active",
                    ],
                )
                .count()
            )

            if total_quantity < active_or_approved_count:

                form.add_error(
                    "total_quantity",
                    (
                        "Total quantity cannot be lower "
                        "than the number of vehicles "
                        "currently reserved or rented."
                    ),
                )

            else:

                try:

                    updated_car = form.save()

                    messages.success(
                        request,
                        (
                            f"{updated_car.name} fleet "
                            "information updated successfully."
                        ),
                    )

                    return redirect(
                        "fleet_management"
                    )

                except ValidationError as error:

                    form.add_error(
                        None,
                        (
                            "Vehicle could not be updated: "
                            f"{error}"
                        ),
                    )

        else:

            messages.error(
                request,
                "Please correct the errors below.",
            )

    else:

        form = FleetVehicleForm(
            instance=car,
        )

    return render(
        request,
        "core/fleet_vehicle_form.html",
        {
            "form": form,
            "car": car,
            "page_title": "Edit Vehicle",
            "submit_text": "Save Changes",
        },
    )


# ============================================================
# FLEET VEHICLE ADD
# ============================================================

@staff_member_required
def fleet_vehicle_add(request):
    """
    Add a new vehicle to the fleet.

    Uses FleetVehicleForm so the same validation rules
    are applied consistently when creating vehicles.
    """

    if request.method == "POST":

        form = FleetVehicleForm(
            request.POST,
            request.FILES,
        )

        if form.is_valid():

            try:

                car = form.save()

                messages.success(
                    request,
                    (
                        f"{car.name} was added to the fleet "
                        "successfully."
                    ),
                )

                return redirect(
                    "fleet_management"
                )

            except ValidationError as error:

                form.add_error(
                    None,
                    (
                        "Vehicle could not be added: "
                        f"{error}"
                    ),
                )

        else:

            messages.error(
                request,
                "Please correct the errors below.",
            )

    else:

        form = FleetVehicleForm()

    return render(
        request,
        "core/fleet_vehicle_form.html",
        {
            "form": form,
            "page_title": "Add Vehicle",
            "submit_text": "Add Vehicle",
        },
    )


# ============================================================
# FLEET VEHICLE DETAIL
# ============================================================

@staff_member_required
def fleet_vehicle_detail(request, car_id):
    """
    Display detailed fleet information for one vehicle.

    Includes:
    - Fleet information
    - Current availability
    - Maintenance information
    - Booking statistics
    - Recent booking history
    """

    car = get_object_or_404(
        Car,
        id=car_id,
    )

    bookings = (
        Booking.objects
        .filter(car=car)
        .select_related("user")
        .order_by("-created_at")
    )

    total_bookings = bookings.count()

    pending_bookings = bookings.filter(
        status="Pending"
    ).count()

    approved_bookings = bookings.filter(
        status="Approved"
    ).count()

    active_bookings = bookings.filter(
        status="Active"
    ).count()

    completed_bookings = bookings.filter(
        status="Completed"
    ).count()

    cancelled_bookings = bookings.filter(
        status="Cancelled"
    ).count()

    rejected_bookings = bookings.filter(
        status="Rejected"
    ).count()

    # --------------------------------------------------------
    # CURRENT FLEET VALUES
    # --------------------------------------------------------

    total_quantity = max(
        0,
        car.total_quantity or 0,
    )

    maintenance_count = max(
        0,
        car.maintenance_count or 0,
    )

    available_quantity = max(
        0,
        car.available_quantity or 0,
    )

    rented_quantity = (
        approved_bookings
        + active_bookings
    )

    if rented_quantity > total_quantity:
        rented_quantity = total_quantity

    # --------------------------------------------------------
    # DETAIL CONTEXT
    # --------------------------------------------------------

    context = {

        "car": car,

        # Recent bookings
        "bookings": bookings[:10],

        # Booking statistics
        "total_bookings": total_bookings,
        "pending_bookings": pending_bookings,
        "approved_bookings": approved_bookings,
        "active_bookings": active_bookings,
        "completed_bookings": completed_bookings,
        "cancelled_bookings": cancelled_bookings,
        "rejected_bookings": rejected_bookings,

        # Fleet statistics
        "total_quantity": total_quantity,
        "available_quantity": available_quantity,
        "maintenance_count": maintenance_count,
        "rented_quantity": rented_quantity,
    }

    return render(
        request,
        "core/fleet_vehicle_detail.html",
        context,
    )


# ============================================================
# FLEET VEHICLE ARCHIVE
# ============================================================

@staff_member_required
@require_POST
def fleet_vehicle_archive(request, car_id):
    """
    Archive a fleet vehicle.

    We do NOT physically delete a vehicle that has booking
    history because historical bookings must continue to
    reference the Car record.

    A vehicle with booking history is therefore marked
    Inactive instead of deleted.
    """

    car = get_object_or_404(
        Car,
        id=car_id,
    )

    

    # --------------------------------------------------------
    # DO NOT ARCHIVE AN ALREADY INACTIVE VEHICLE
    # --------------------------------------------------------

    if car.fleet_status == "Inactive":

        messages.info(
            request,
            f"{car.name} is already archived.",
        )

        return redirect(
            "fleet_management"
        )

    # --------------------------------------------------------
    # NEVER ARCHIVE A VEHICLE CURRENTLY RENTED
    # --------------------------------------------------------

    active_booking_exists = (
        Booking.objects
        .filter(
            car=car,
            status="Active",
        )
        .exists()
    )

    if active_booking_exists:

        messages.error(
            request,
            (
                f"{car.name} cannot be archived while "
                "it is currently rented."
            ),
        )

        return redirect(
            "fleet_management"
        )

    # --------------------------------------------------------
    # NEVER ARCHIVE A VEHICLE WITH AN APPROVED UPCOMING
    # RESERVATION
    # --------------------------------------------------------

    approved_booking_exists = (
        Booking.objects
        .filter(
            car=car,
            status="Approved",
        )
        .exists()
    )

    if approved_booking_exists:

        messages.error(
            request,
            (
                f"{car.name} cannot be archived because "
                "it has an approved reservation."
            ),
        )

        return redirect(
            "fleet_management"
        )

    # --------------------------------------------------------
    # ARCHIVE
    # --------------------------------------------------------

    vehicle_name = car.name

    car.fleet_status = "Inactive"

    car.save(
        update_fields=[
            "fleet_status",
        ]
    )

    messages.success(
        request,
        (
            f"{vehicle_name} has been archived "
            "successfully."
        ),
    )

    return redirect(
        "fleet_management"
    )


# ============================================================
# BACKWARD-COMPATIBILITY ALIAS
# ============================================================
#
# If your existing template or URL configuration still uses
# fleet_vehicle_delete, keep this wrapper temporarily.
#
# This prevents existing links from breaking while we migrate
# the project to the clearer "archive" terminology.
# ============================================================

@staff_member_required
def fleet_vehicle_delete(request, car_id):

    return fleet_vehicle_archive(
        request,
        car_id,
    )
# ============================================================
# BOOKING MANAGEMENT
# ============================================================
@staff_member_required
def booking_management(request):
    # Keep automatic rental lifecycle current.
    update_rental_statuses()

    # --------------------------------------------------------
    # BASE QUERY
    # --------------------------------------------------------
    bookings = (
        Booking.objects
        .select_related("car", "user")
        .all()
        .order_by("-created_at")
    )

    # --------------------------------------------------------
    # SEARCH
    # --------------------------------------------------------
    search = request.GET.get("search", "").strip()

    if search:
        bookings = bookings.filter(
            Q(first_name__icontains=search)
            | Q(last_name__icontains=search)
            | Q(email__icontains=search)
            | Q(car__name__icontains=search)
            | Q(car_type__icontains=search)
        )

    # --------------------------------------------------------
    # STATUS FILTER
    # --------------------------------------------------------
    status = request.GET.get("status", "").strip()

    allowed_statuses = [
        "Pending",
        "Approved",
        "Active",
        "Completed",
        "Cancelled",
        "Rejected",
    ]

    if status in allowed_statuses:
        bookings = bookings.filter(status=status)

    # --------------------------------------------------------
    # BOOKING STATISTICS
    # --------------------------------------------------------
    total_bookings = Booking.objects.count()

    pending_bookings = Booking.objects.filter(
        status="Pending"
    ).count()

    approved_bookings = Booking.objects.filter(
        status="Approved"
    ).count()

    active_bookings = Booking.objects.filter(
        status="Active"
    ).count()

    completed_bookings = Booking.objects.filter(
        status="Completed"
    ).count()

    cancelled_bookings = Booking.objects.filter(
        status="Cancelled"
    ).count()

    rejected_bookings = Booking.objects.filter(
        status="Rejected"
    ).count()

    # Number currently displayed after search/filter
    filtered_bookings = bookings.count()

    # --------------------------------------------------------
    # CONTEXT
    # --------------------------------------------------------
    context = {
        "bookings": bookings,

        # Statistics
        "total_bookings": total_bookings,
        "pending_bookings": pending_bookings,
        "approved_bookings": approved_bookings,
        "active_bookings": active_bookings,
        "completed_bookings": completed_bookings,
        "cancelled_bookings": cancelled_bookings,
        "rejected_bookings": rejected_bookings,

        # Filter result count
        "filtered_bookings": filtered_bookings,

        # Current filters
        "search": search,
        "status": status,
    }

    return render(
        request,
        "core/booking_management.html",
        context,
    )


# ============================================================
# BOOKING STATUS UPDATE
# ============================================================

@staff_member_required
@require_POST
def update_booking_status(request, booking_id, status):

    allowed_statuses = {
        "Approved",
        "Rejected",
        "Cancelled",
    }

    if status not in allowed_statuses:
        messages.error(
            request,
            "Invalid booking status."
        )
        return redirect("booking_management")

    with transaction.atomic():

        booking = get_object_or_404(
            Booking.objects.select_related(
                "car",
                "user",
            ),
            id=booking_id,
        )

        # --------------------------------------------------------
        # ONLY PENDING BOOKINGS CAN BE DECIDED
        # --------------------------------------------------------

        if booking.status != "Pending":

            messages.error(
                request,
                (
                    f"Booking #{booking.id} cannot be "
                    f"changed from {booking.status} "
                    f"to {status}."
                ),
            )

            return redirect("booking_management")

        # --------------------------------------------------------
        # APPROVAL VALIDATION
        # --------------------------------------------------------

        if status == "Approved":

            if not booking.driver_license:

                messages.error(
                    request,
                    "Customer driver license is missing.",
                )

                return redirect("booking_management")

            if not booking.national_id:

                messages.error(
                    request,
                    "Customer national ID is missing.",
                )

                return redirect("booking_management")

            if booking.document_status != "Verified":

                messages.error(
                    request,
                    (
                        "Customer documents must be "
                        "verified before approval."
                    ),
                )

                return redirect("booking_management")

            if not booking.car:

                messages.error(
                    request,
                    "This booking has no assigned car.",
                )

                return redirect("booking_management")

            # ----------------------------------------------------
            # VEHICLE AVAILABILITY
            # ----------------------------------------------------

            available = booking.car.available_for_dates(
                booking.pickup_date,
                booking.dropoff_date,
            )

            if available <= 0:

                messages.error(
                    request,
                    (
                        "This car is not available "
                        "for the selected dates."
                    ),
                )

                return redirect("booking_management")

        # --------------------------------------------------------
        # DO NOT CHANGE DOCUMENT STATUS HERE
        # --------------------------------------------------------

        booking.status = status

        try:

            booking.full_clean()

            booking.save()

        except ValidationError as error:

            messages.error(
                request,
                (
                    "Booking could not be changed: "
                    f"{error}"
                ),
            )

            return redirect("booking_management")

    # ------------------------------------------------------------
    # SUCCESS
    # ------------------------------------------------------------

    messages.success(
        request,
        (
            f"Booking #{booking.id} "
            f"changed to {status}."
        ),
    )

    return redirect("booking_management")


@staff_member_required
@require_POST
def verify_documents(
    request,
    booking_id,
    action,
):
    # --------------------------------------------------------
    # ONLY POST REQUESTS MAY CHANGE DOCUMENT STATUS
    # --------------------------------------------------------

    if request.method != "POST":
        messages.error(
            request,
            "Invalid document verification request.",
        )
        return redirect("booking_management")

    booking = get_object_or_404(
        Booking,
        id=booking_id,
    )

    # --------------------------------------------------------
    # VERIFY DOCUMENTS
    # --------------------------------------------------------

    if action == "verify":

        if not booking.driver_license:
            messages.error(
                request,
                "Driver license is missing.",
            )
            return redirect(
                "booking_management"
            )

        if not booking.national_id:
            messages.error(
                request,
                "National ID is missing.",
            )
            return redirect(
                "booking_management"
            )

        booking.document_status = "Verified"

        booking.save(
            update_fields=[
                "document_status",
            ]
        )

        messages.success(
            request,
            (
                f"Documents for booking "
                f"#{booking.id} verified successfully."
            ),
        )

    # --------------------------------------------------------
    # REJECT DOCUMENTS
    # --------------------------------------------------------

    elif action == "reject":

        booking.document_status = "Rejected"

        booking.save(
            update_fields=[
                "document_status",
            ]
        )

        messages.warning(
            request,
            (
                f"Documents for booking "
                f"#{booking.id} rejected."
            ),
        )

    # --------------------------------------------------------
    # INVALID ACTION
    # --------------------------------------------------------

    else:
        messages.error(
            request,
            "Invalid document action.",
        )

    return redirect(
        "booking_management"
    )
# ============================================================
# RENTAL ACTIONS
# ============================================================
@staff_member_required
@require_POST
def rental_action(
    request,
    booking_id,
    action,
):

    booking = get_object_or_404(
        Booking.objects.select_related(
            "car",
            "user",
        ),
        id=booking_id,
    )

    # ========================================================
    # START RENTAL
    # ========================================================

    if action == "start":

        if booking.status != "Approved":

            messages.error(
                request,
                (
                    f"Booking #{booking.id} cannot "
                    f"start because its current status "
                    f"is {booking.status}."
                ),
            )

            return redirect("booking_management")

        if booking.payment_status != "Paid":

            messages.error(
                request,
                (
                    "Payment must be completed "
                    "before the rental can start."
                ),
            )

            return redirect("booking_management")

        if booking.document_status != "Verified":

            messages.error(
                request,
                (
                    "Customer documents must be "
                    "verified before rental pickup."
                ),
            )

            return redirect("booking_management")

        if not booking.car:

            messages.error(
                request,
                "This booking has no assigned vehicle."
            )

            return redirect("booking_management")

        booking.status = "Active"
        booking.pickup_completed = timezone.now()

        booking.save(
            update_fields=[
                "status",
                "pickup_completed",
            ]
        )

        messages.success(
            request,
            (
                f"Rental for booking #{booking.id} "
                "started successfully."
            ),
        )

    # ========================================================
    # COMPLETE RENTAL
    # ========================================================

    elif action == "complete":

        if booking.status != "Active":

            messages.error(
                request,
                (
                    f"Booking #{booking.id} cannot "
                    f"be completed because its current "
                    f"status is {booking.status}."
                ),
            )

            return redirect("booking_management")

        booking.status = "Completed"
        booking.return_completed = timezone.now()

        booking.save(
            update_fields=[
                "status",
                "return_completed",
            ]
        )

        messages.success(
            request,
            (
                f"Rental for booking #{booking.id} "
                "completed successfully."
            ),
        )

    else:

        messages.error(
            request,
            "Invalid rental action.",
        )

    return redirect("booking_management")


# ============================================================
# PAYMENT MANAGEMENT
# ============================================================

@staff_member_required
def payment_management(request):

    bookings = (
        Booking.objects
        .select_related(
            "car",
            "user",
        )
        .all()
        .order_by("-created_at")
    )

    search = request.GET.get(
        "search",
        "",
    ).strip()

    payment_status = request.GET.get(
        "payment_status",
        "",
    ).strip()

    if search:

        bookings = bookings.filter(
            Q(first_name__icontains=search)
            | Q(last_name__icontains=search)
            | Q(email__icontains=search)
            | Q(car__name__icontains=search)
            | Q(payment_reference__icontains=search)
        )

    allowed_payment_statuses = {
        "Pending",
        "Paid",
        "Failed",
        "Refunded",
    }

    if payment_status in allowed_payment_statuses:

        bookings = bookings.filter(
            payment_status=payment_status
        )

    context = {

        "bookings": bookings,

        "search": search,

        "payment_status": payment_status,

        "total_payments": Booking.objects.exclude(
            payment_status__isnull=True
        ).count(),

        "paid_payments": Booking.objects.filter(
            payment_status="Paid"
        ).count(),

        "pending_payments": Booking.objects.filter(
            payment_status="Pending"
        ).count(),

        "failed_payments": Booking.objects.filter(
            payment_status="Failed"
        ).count(),

        "refunded_payments": Booking.objects.filter(
            payment_status="Refunded"
        ).count(),
    }

    return render(
        request,
        "core/payment_management.html",
        context,
    )
# ============================================================
# MARK PAYMENT AS PAID
# ============================================================

@staff_member_required
@require_POST
def mark_payment_paid(request, booking_id):

    if request.method != "POST":
        messages.error(
            request,
            "Invalid payment request."
        )
        return redirect("booking_management")

    booking = get_object_or_404(
        Booking,
        id=booking_id
    )

    # -------------------------------------------------
    # ALREADY PAID
    # -------------------------------------------------

    if booking.payment_status == "Paid":

        messages.info(
            request,
            f"Booking #{booking.id} is already paid."
        )

        return redirect("booking_management")

    # -------------------------------------------------
    # PAYMENT METHOD REQUIRED
    # -------------------------------------------------

    if not booking.payment_method:

        messages.error(
            request,
            (
                f"Booking #{booking.id} has no payment "
                "method selected."
            )
        )

        return redirect("booking_management")

    # -------------------------------------------------
    # CASH PAYMENT
    # -------------------------------------------------

    if booking.payment_method == "Cash":

        booking.payment_status = "Paid"

        booking.payment_reference = (
            f"CASH-{booking.id}"
        )

        booking.payment_date = timezone.now()

    # -------------------------------------------------
    # ONLINE PAYMENT
    # -------------------------------------------------

    elif booking.payment_method in [
        "Chapa",
        "Telebirr",
    ]:

        if not booking.payment_reference:

            messages.error(
                request,
                (
                    "An online payment reference is "
                    "required before marking this payment "
                    "as paid."
                )
            )

            return redirect("booking_management")

        booking.payment_status = "Paid"

        booking.payment_date = timezone.now()

    # -------------------------------------------------
    # UNKNOWN PAYMENT METHOD
    # -------------------------------------------------

    else:

        messages.error(
            request,
            "Invalid payment method."
        )

        return redirect("booking_management")

    # -------------------------------------------------
    # SAVE PAYMENT
    # -------------------------------------------------

    try:

        booking.save()

    except ValidationError as error:

        messages.error(
            request,
            f"Payment could not be updated: {error}"
        )

        return redirect("booking_management")

    messages.success(
        request,
        (
            f"Payment for booking #{booking.id} "
            f"marked as paid successfully."
        )
    )

    return redirect("booking_management")