from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.models import DeliveryLog
from typing import List, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel

router = APIRouter()

class DeliveryStatus(BaseModel):
    webhook_id: str
    status: str
    attempts: int
    last_attempt: datetime
    is_success: bool
    error_message: Optional[str] = None

    class Config:
        orm_mode = True

class DeliveryLogResponse(BaseModel):
    webhook_id: str
    event_type: str
    status_code: int
    is_success: bool
    error_message: Optional[str] = None
    created_at: datetime

    class Config:
        orm_mode = True

@router.get("/{webhook_id}", response_model=DeliveryStatus)
def get_delivery_status(webhook_id: str, db: Session = Depends(get_db)):
    try:
        # Get all delivery attempts for this webhook
        attempts = db.query(DeliveryLog).filter(
            DeliveryLog.webhook_id == webhook_id
        ).order_by(DeliveryLog.created_at.desc()).all()

        if not attempts:
            raise HTTPException(status_code=404, detail="Webhook not found")

        last_attempt = attempts[0]
        success_count = sum(1 for attempt in attempts if attempt.is_success)

        return DeliveryStatus(
            webhook_id=webhook_id,
            status="success" if success_count > 0 else "failed",
            attempts=len(attempts),
            last_attempt=last_attempt.created_at,
            is_success=last_attempt.is_success,
            error_message=last_attempt.error_message
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/logs/{subscription_id}", response_model=List[DeliveryLogResponse])
def get_delivery_logs(
    subscription_id: int,
    db: Session = Depends(get_db),
    days: int = 7
):
    try:
        # Get delivery logs for the subscription within the specified time range
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        logs = db.query(DeliveryLog).filter(
            DeliveryLog.subscription_id == subscription_id,
            DeliveryLog.created_at >= cutoff_date
        ).order_by(DeliveryLog.created_at.desc()).all()

        return [
            DeliveryLogResponse(
                webhook_id=log.webhook_id,
                event_type=log.event_type,
                status_code=log.status_code,
                is_success=log.is_success,
                error_message=log.error_message,
                created_at=log.created_at
            )
            for log in logs
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 