import logging
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    """
    Custom exception handler to standardize API error responses across all endpoints.
    Formats errors into a consistent JSON envelope:
    {
        "success": false,
        "status_code": <int>,
        "message": "<summary_message>",
        "errors": <detailed_errors_dict_or_list_or_null>
    }
    """
    response = exception_handler(exc, context)

    if response is not None:
        custom_data = {
            "success": False,
            "status_code": response.status_code,
            "message": "An error occurred while processing your request.",
            "errors": None,
        }

        # Determine appropriate high-level message
        if response.status_code == status.HTTP_400_BAD_REQUEST:
            custom_data["message"] = "Validation failed. Please verify your input."
        elif response.status_code == status.HTTP_401_UNAUTHORIZED:
            custom_data["message"] = "Authentication credentials were invalid or not provided."
        elif response.status_code == status.HTTP_403_FORBIDDEN:
            custom_data["message"] = "You do not have permission to perform this action."
        elif response.status_code == status.HTTP_404_NOT_FOUND:
            custom_data["message"] = "The requested resource was not found."
        elif response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED:
            custom_data["message"] = "HTTP method not allowed on this endpoint."

        # Process the exception data details
        if isinstance(response.data, dict):
            if "detail" in response.data and len(response.data) == 1:
                custom_data["message"] = str(response.data["detail"])
            else:
                custom_data["errors"] = response.data
        elif isinstance(response.data, list):
            custom_data["errors"] = response.data
        else:
            custom_data["message"] = str(response.data)

        response.data = custom_data
        return response

    # If unhandled by standard DRF handler (e.g. 500 error)
    logger.exception("Unhandled server error: %s", exc)
    return Response(
        {
            "success": False,
            "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
            "message": "An unexpected internal server error occurred.",
            "errors": str(exc),
        },
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )
