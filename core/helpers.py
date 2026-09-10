from datetime import datetime
from django.utils import timezone


def validate_booking_dates(request):

    try:
        pickup = datetime.strptime(
            request.POST.get("pickup_date"),
            "%Y-%m-%d"
        ).date()

        dropoff = datetime.strptime(
            request.POST.get("dropoff_date"),
            "%Y-%m-%d"
        ).date()

    except (ValueError, TypeError):

        raise ValueError(
            "Please select valid pickup and drop-off dates."
        )


    today = timezone.now().date()


    if pickup < today:

        raise ValueError(
            "Please select a valid pickup date. "
            "The pickup date cannot be in the past."
        )


    if dropoff <= pickup:

        raise ValueError(
            "Please select a valid drop-off date. "
            "It must be after the pickup date."
        )


    return pickup, dropoff