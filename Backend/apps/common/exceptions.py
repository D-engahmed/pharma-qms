from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
import logging

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    """Custom exception handler for consistent error responses"""
    response = exception_handler(exc, context)
    
    if response is not None:
        custom_response = {
            'error': {
                'code': response.status_code,
                'message': str(exc),
                'details': response.data
            }
        }
        return Response(custom_response, status=response.status_code)
    
    # Log unhandled exceptions
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return Response(
        {'error': {'code': 500, 'message': 'Internal server error'}},
        status=status.HTTP_500_INTERNAL_SERVER_ERROR
    )