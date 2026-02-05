from pydantic import BaseModel, field_validator
from typing import Literal, Optional

ALLOWED_STATUSES = Literal['Open', 'In Progress', 'Closed']
ALLOWED_PRIORITIES = Literal['Low', 'Medium', 'High']
ALLOWED_CATEGORIES = Literal['General']

class TicketCreateSchema(BaseModel):
    title: str
    description: str
    priority: ALLOWED_PRIORITIES
    category: ALLOWED_CATEGORIES
    customer_id: int

    @field_validator('title')
    @classmethod
    def title_not_empty(cls, v):
        if not v.strip():
            raise ValueError('Title cannot be empty.')
        return v.strip()

class TicketUpdateSchema(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[ALLOWED_STATUSES] = None
    priority: Optional[ALLOWED_PRIORITIES] = None
    category: Optional[ALLOWED_CATEGORIES] = None
    customer_id: Optional[int] = None
    assigned_to_id: Optional[int] = None