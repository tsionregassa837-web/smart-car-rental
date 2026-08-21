from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from django.db.models import Sum
from django.contrib.auth.models import User

from .models import Booking, Car


@staff_member_required
def reports_dashboard(request):

    total_bookings = Booking.objects.count()

    total_customers = User.objects.filter(
        is_staff=False
    ).count()

    total_cars = Car.objects.count()

    available_cars = sum(
        car.available_quantity
        for car in Car.objects.all()
    )

    active_rentals = Booking.objects.filter(
        status="Active"
    ).count()

    completed_rentals = Booking.objects.filter(
        status="Completed"
    ).count()

    cancelled_bookings = Booking.objects.filter(
        status="Cancelled"
    ).count()

    total_revenue = (
        Booking.objects.filter(
            payment_status="Paid"
        ).aggregate(
            total=Sum("total_price")
        )["total"] or 0
    )

    context = {
        "total_bookings": total_bookings,
        "total_customers": total_customers,
        "total_cars": total_cars,
        "available_cars": available_cars,
        "active_rentals": active_rentals,
        "completed_rentals": completed_rentals,
        "cancelled_bookings": cancelled_bookings,
        "total_revenue": total_revenue,
    }

    return render(
        request,
        "core/reports_dashboard.html",
        context,
    )