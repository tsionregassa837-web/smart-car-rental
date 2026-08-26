import logging

logger = logging.getLogger(__name__)


class RentalStatusMiddleware:
    """
    Middleware for Smart Car Rental.
    Does not automatically mutate booking states; lifecycle transitions
    (Approved -> Active -> Completed) are executed manually by staff.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response