import logging
from rest_framework.response import Response
from rest_framework import status

logger = logging.getLogger(__name__)

class ExceptionLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_exception(self, request, exception):
        logger.exception(f"Server error: {exception}")
        return Response(
            {"error": "Internal server error", "detail": str(exception)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
