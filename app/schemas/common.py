# app/schemas/common.py
from pydantic import BaseModel, ConfigDict


class BaseSchema(BaseModel):
    """
    Base schema with shared Pydantic configuration.
    """

    model_config = ConfigDict(
        from_attributes=True,
        use_enum_values=True,
        extra="forbid",
    )
