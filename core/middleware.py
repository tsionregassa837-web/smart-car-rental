from django.db import transaction
from .views import update_rental_statuses


class RentalStatusMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        try:
            # Automatically update rental statuses.
            # If an existing booking fails model validation,
            # do not prevent the requested page from loading.
            update_rental_statuses()

        except Exception as e:
            # Keep the website running if an old booking contains
            # data that no longer passes current model validation.
            print(
                "Rental status update skipped:",
                e
            )

        response = self.get_response(request)

        return response