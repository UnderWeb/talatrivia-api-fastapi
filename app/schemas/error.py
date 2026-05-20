# app/schemas/error.py
from .common import BaseSchema


class ErrorResponse(BaseSchema):
    """
    Standardized API error response.
    """

    detail: str
