from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

class DeliveryLogResponse(BaseModel):
    id: int
    subscription_id: int
    webhook_id: str
    payload: Dict[str, Any]
    attempt_number: int
    status_code: Optional[int] = None
    response_body: Optional[str] = None
    error_message: Optional[str] = None
    is_success: bool
    created_at: datetime

    class Config:
        orm_mode = True 