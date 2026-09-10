from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User
from django.db.models import Sum, Count
from django.db.models.functions import TruncMonth
from django.shortcuts import render
from django.utils import timezone

from .models import Booking, Car


@staff_member_required
def reports_dashboard(request):

    # ============================================================
    # BASE QUERYSETS
    # ============================================================

    bookings = Booking.objects.all()
    cars = Car.objects.all()

    customers = User.objects.filter(
        is_staff=False,
        is_superuser=False
    )

    # ============================================================
    # BOOKING KPIs
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

    completed_rentals = bookings.filter(
        status="Completed"
    ).count()

    cancelled_bookings = bookings.filter(
        status="Cancelled"
    ).count()

    rejected_bookings = bookings.filter(
        status="Rejected"
    ).count()

    # ============================================================
    # CUSTOMER KPIs
    # ============================================================

    total_customers = customers.count()

    active_customers = customers.filter(
        is_active=True
    ).count()

    inactive_customers = customers.filter(
        is_active=False
    ).count()

    # IMPORTANT:
    # Booking.user does not define related_name.
    # In this project Django exposes the reverse query
    # name as "booking", NOT "booking_set".
    customers_with_bookings = customers.filter(
        booking__isnull=False
    ).distinct().count()

    customers_without_bookings = max(
        total_customers - customers_with_bookings,
        0
    )

    # ============================================================
    # FLEET KPIs
    # ============================================================

    total_vehicle_types = cars.count()

    total_fleet_units = sum(
        car.total_quantity
        for car in cars
    )

    # Actual available units based on your Car.available_quantity
    available_cars = sum(
        car.available_quantity
        for car in cars
    )

    # Actual rented units
    rented_cars = sum(
        max(
            car.total_quantity - car.available_quantity,
            0
        )
        for car in cars
        if car.fleet_status not in [
            "Maintenance",
            "Inactive"
        ]
    )

    # Maintenance units
    maintenance_cars = cars.filter(
        fleet_status="Maintenance"
    ).aggregate(
        total=Sum("total_quantity")
    )["total"] or 0

    # Inactive units
    inactive_cars = cars.filter(
        fleet_status="Inactive"
    ).aggregate(
        total=Sum("total_quantity")
    )["total"] or 0

    # ============================================================
    # FLEET UTILIZATION
    # ============================================================

    if total_fleet_units > 0:
        fleet_utilization = round(
            (rented_cars / total_fleet_units) * 100,
            1
        )
    else:
        fleet_utilization = 0

    # ============================================================
    # PAYMENT / REVENUE KPIs
    # ============================================================

    paid_bookings = bookings.filter(
        payment_status="Paid"
    )

    total_revenue = (
        paid_bookings.aggregate(
            total=Sum("total_price")
        )["total"]
        or 0
    )

    pending_revenue = (
        bookings.filter(
            payment_status="Pending"
        ).aggregate(
            total=Sum("total_price")
        )["total"]
        or 0
    )

    refunded_amount = (
        bookings.filter(
            payment_status="Refunded"
        ).aggregate(
            total=Sum("total_price")
        )["total"]
        or 0
    )

    failed_payments = bookings.filter(
        payment_status="Failed"
    ).count()

    paid_payment_count = paid_bookings.count()

    # ============================================================
    # AVERAGE BOOKING VALUE
    # ============================================================

    if paid_payment_count > 0:

        average_booking_value = (
            total_revenue / paid_payment_count
        )

    else:

        average_booking_value = 0

    # ============================================================
    # BOOKING STATUS CHART
    # ============================================================

    booking_status_data = {
        "Pending": pending_bookings,
        "Approved": approved_bookings,
        "Active": active_rentals,
        "Completed": completed_rentals,
        "Cancelled": cancelled_bookings,
        "Rejected": rejected_bookings,
    }

    # ============================================================
    # PAYMENT STATUS CHART
    # ============================================================

    payment_status_data = {

        "Paid": bookings.filter(
            payment_status="Paid"
        ).count(),

        "Pending": bookings.filter(
            payment_status="Pending"
        ).count(),

        "Failed": bookings.filter(
            payment_status="Failed"
        ).count(),

        "Refunded": bookings.filter(
            payment_status="Refunded"
        ).count(),
    }

    # ============================================================
    # FLEET STATUS CHART
    # ============================================================
    #
    # IMPORTANT:
    # Available and Rented use ACTUAL fleet units.
    # Maintenance and Inactive use their stored fleet quantities.
    #
    # This matches the availability logic in your Car model.
    # ============================================================

    fleet_status_data = {

        "Available": available_cars,

        "Rented": rented_cars,

        "Maintenance": maintenance_cars,

        "Inactive": inactive_cars,
    }

    # ============================================================
    # CUSTOMER ACTIVITY CHART
    # ============================================================

    customer_activity_data = {

        "With Rentals": customers_with_bookings,

        "No Rentals": customers_without_bookings,
    }

    # ============================================================
    # MONTHLY REVENUE
    # ============================================================

    monthly_revenue_queryset = (
        paid_bookings
        .filter(
            payment_date__isnull=False
        )
        .annotate(
            month=TruncMonth("payment_date")
        )
        .values("month")
        .annotate(
            revenue=Sum("total_price")
        )
        .order_by("month")
    )

    monthly_revenue_labels = []

    monthly_revenue_values = []

    for item in monthly_revenue_queryset:

        if item["month"]:

            monthly_revenue_labels.append(
                item["month"].strftime("%b %Y")
            )

            monthly_revenue_values.append(
                float(item["revenue"] or 0)
            )

    # ============================================================
    # MONTHLY BOOKINGS
    # ============================================================

    monthly_booking_queryset = (
        bookings
        .annotate(
            month=TruncMonth("created_at")
        )
        .values("month")
        .annotate(
            total=Count("id")
        )
        .order_by("month")
    )

    monthly_booking_labels = []

    monthly_booking_values = []

    for item in monthly_booking_queryset:

        if item["month"]:

            monthly_booking_labels.append(
                item["month"].strftime("%b %Y")
            )

            monthly_booking_values.append(
                item["total"]
            )

    # ============================================================
    # TOP VEHICLES
    # ============================================================
    #
    # IMPORTANT:
    # Car.booking is the reverse query name in your project.
    # Do NOT use booking_set.
    # ============================================================

    top_cars = (
        cars
        .annotate(
            booking_count=Count(
                "booking",
                distinct=True
            )
        )
        .order_by(
            "-booking_count",
            "name"
        )[:5]
    )

    # ============================================================
    # RECENT BOOKINGS
    # ============================================================

    recent_bookings = (
        bookings
        .select_related(
            "car",
            "user"
        )
        .order_by(
            "-created_at"
        )[:8]
    )

    # ============================================================
    # PAYMENT METHOD REPORT
    # ============================================================

    chapa_payments = bookings.filter(
        payment_status="Paid",
        payment_method="Chapa"
    ).count()

    telebirr_payments = bookings.filter(
        payment_status="Paid",
        payment_method="Telebirr"
    ).count()

    cash_payments = bookings.filter(
        payment_status="Paid",
        payment_method="Cash"
    ).count()

    payment_method_data = {

        "Chapa": chapa_payments,

        "Telebirr": telebirr_payments,

        "Cash": cash_payments,
    }

    # ============================================================
    # BOOKING COMPLETION RATE
    # ============================================================

    if total_bookings > 0:

        completion_rate = round(
            (
                completed_rentals
                / total_bookings
            ) * 100,
            1
        )

    else:

        completion_rate = 0

    # ============================================================
    # CANCELLATION RATE
    # ============================================================

    if total_bookings > 0:

        cancellation_rate = round(
            (
                cancelled_bookings
                / total_bookings
            ) * 100,
            1
        )

    else:

        cancellation_rate = 0

    # ============================================================
    # PAYMENT SUCCESS RATE
    # ============================================================

    payment_attempts = bookings.exclude(
        payment_status="Pending"
    ).count()

    if payment_attempts > 0:

        payment_success_rate = round(
            (
                paid_payment_count
                / payment_attempts
            ) * 100,
            1
        )

    else:

        payment_success_rate = 0

    # ============================================================
    # REPORT DATE
    # ============================================================

    report_date = timezone.now()

    # ============================================================
    # CONTEXT
    # ============================================================

    context = {

        # --------------------------------------------------------
        # BOOKING
        # --------------------------------------------------------

        "total_bookings": total_bookings,

        "pending_bookings": pending_bookings,

        "approved_bookings": approved_bookings,

        "active_rentals": active_rentals,

        "completed_rentals": completed_rentals,

        "cancelled_bookings": cancelled_bookings,

        "rejected_bookings": rejected_bookings,

        "completion_rate": completion_rate,

        "cancellation_rate": cancellation_rate,

        # --------------------------------------------------------
        # CUSTOMERS
        # --------------------------------------------------------

        "total_customers": total_customers,

        "active_customers": active_customers,

        "inactive_customers": inactive_customers,

        "customers_with_bookings": customers_with_bookings,

        "customers_without_bookings": customers_without_bookings,

        # --------------------------------------------------------
        # FLEET
        # --------------------------------------------------------

        "total_vehicle_types": total_vehicle_types,

        "total_fleet_units": total_fleet_units,

        "available_cars": available_cars,

        "rented_cars": rented_cars,

        "maintenance_cars": maintenance_cars,

        "inactive_cars": inactive_cars,

        "fleet_utilization": fleet_utilization,

        # --------------------------------------------------------
        # PAYMENTS
        # --------------------------------------------------------

        "total_revenue": total_revenue,

        "pending_revenue": pending_revenue,

        "refunded_amount": refunded_amount,

        "failed_payments": failed_payments,

        "paid_payment_count": paid_payment_count,

        "average_booking_value": average_booking_value,

        "payment_success_rate": payment_success_rate,

        # --------------------------------------------------------
        # CHART DATA
        # --------------------------------------------------------

        "booking_status_data": booking_status_data,

        "payment_status_data": payment_status_data,

        "fleet_status_data": fleet_status_data,

        "customer_activity_data": customer_activity_data,

        "payment_method_data": payment_method_data,

        # --------------------------------------------------------
        # MONTHLY CHARTS
        # --------------------------------------------------------

        "monthly_revenue_labels": monthly_revenue_labels,

        "monthly_revenue_values": monthly_revenue_values,

        "monthly_booking_labels": monthly_booking_labels,

        "monthly_booking_values": monthly_booking_values,

        # --------------------------------------------------------
        # TABLES
        # --------------------------------------------------------

        "top_cars": top_cars,

        "recent_bookings": recent_bookings,

        # --------------------------------------------------------
        # META
        # --------------------------------------------------------

        "report_date": report_date,
    }

    return render(
        request,
        "core/reports_dashboard.html",
        context
    )