from pydantic import BaseModel, HttpUrl, field_validator
from typing import Optional, List
from datetime import datetime

class SubscriptionBase(BaseModel):
    target_url: str
    secret_key: Optional[str] = None
    event_types: Optional[List[str]] = None

    @field_validator('target_url')
    def validate_url(cls, v):
        if not v.startswith(('http://', 'https://')):
            raise ValueError('URL must start with http:// or https://')
        return v

class SubscriptionCreate(SubscriptionBase):
    pass

class SubscriptionResponse(SubscriptionBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True 