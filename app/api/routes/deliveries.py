from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.session import get_db
from app.models.models import DeliveryLog
from app.schemas.delivery import DeliveryLogResponse

router = APIRouter()

@router.get("/{webhook_id}", response_model=List[DeliveryLogResponse])
def get_delivery_status(
    webhook_id: str,
    db: Session = Depends(get_db)
):
    logs = db.query(DeliveryLog).filter(
        DeliveryLog.webhook_id == webhook_id
    ).order_by(DeliveryLog.created_at.desc()).all()
    
    if not logs:
        raise HTTPException(status_code=404, detail="No delivery logs found for this webhook")
    
    return logs

@router.get("/subscription/{subscription_id}", response_model=List[DeliveryLogResponse])
def get_subscription_deliveries(
    subscription_id: int,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    logs = db.query(DeliveryLog).filter(
        DeliveryLog.subscription_id == subscription_id
    ).order_by(DeliveryLog.created_at.desc()).limit(limit).all()
    
    return logs 