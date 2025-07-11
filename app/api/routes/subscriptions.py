from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.session import get_db
from app.models.models import Subscription, DeliveryLog
from app.schemas.subscription import SubscriptionCreate, SubscriptionResponse
from app.core.cache import get_cache, Cache
from app.core.security import encrypt_secret
from datetime import datetime
from pydantic import BaseModel
import hmac
import hashlib
import json

router = APIRouter()

class DeleteResponse(BaseModel):
    message: str

class SignatureRequest(BaseModel):
    payload: dict
    secret_key: str

class SignatureResponse(BaseModel):
    signature: str
    headers: dict
    example_request: dict

@router.post("/", response_model=SubscriptionResponse)
def create_subscription(subscription: SubscriptionCreate, db: Session = Depends(get_db)):
    # Encrypt the secret key if provided
    if subscription.secret_key:
        encrypted_secret = encrypt_secret(subscription.secret_key)
    else:
        encrypted_secret = None
    
    db_subscription = Subscription(
        target_url=subscription.target_url,
        secret_key=encrypted_secret,
        event_types=subscription.event_types,
        is_active=True,
        created_at=datetime.utcnow()
    )
    db.add(db_subscription)
    db.commit()
    db.refresh(db_subscription)
    
    # Return the original secret key in the response (only once)
    response = SubscriptionResponse.from_orm(db_subscription)
    response.secret_key = subscription.secret_key
    return response

@router.get("/{subscription_id}", response_model=SubscriptionResponse)
def get_subscription(subscription_id: int, db: Session = Depends(get_db)):
    subscription = db.query(Subscription).filter(Subscription.id == subscription_id).first()
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")
    
    # Create response without exposing the secret key
    response = SubscriptionResponse.from_orm(subscription)
    response.secret_key = None  # Never expose the secret key in responses
    return response

@router.put("/{subscription_id}", response_model=SubscriptionResponse)
def update_subscription(
    subscription_id: int,
    subscription: SubscriptionCreate,
    db: Session = Depends(get_db)
):
    db_subscription = db.query(Subscription).filter(Subscription.id == subscription_id).first()
    if not db_subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")
    
    # Encrypt new secret key if provided
    if subscription.secret_key:
        encrypted_secret = encrypt_secret(subscription.secret_key)
    else:
        # Keep existing secret key
        encrypted_secret = db_subscription.secret_key
    
    # Update fields
    db_subscription.target_url = subscription.target_url
    db_subscription.secret_key = encrypted_secret
    db_subscription.event_types = subscription.event_types
    
    db_subscription.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_subscription)
    
    # Return response without exposing the secret key
    response = SubscriptionResponse.from_orm(db_subscription)
    response.secret_key = None
    return response

@router.delete("/{subscription_id}", response_model=DeleteResponse)
def delete_subscription(subscription_id: int, db: Session = Depends(get_db)):
    try:
        subscription = db.query(Subscription).filter(Subscription.id == subscription_id).first()
        if not subscription:
            raise HTTPException(status_code=404, detail="Subscription not found")
        
        # Delete associated delivery logs first
        db.query(DeliveryLog).filter(DeliveryLog.subscription_id == subscription_id).delete()
        
        # Now delete the subscription
        db.delete(subscription)
        db.commit()
        return {"message": "Subscription and associated delivery logs deleted successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error deleting subscription: {str(e)}")

@router.post("/generate-signature", response_model=SignatureResponse)
def generate_signature(request: SignatureRequest):
    try:
        # Convert payload to bytes with sorted keys for consistent hashing
        payload_bytes = json.dumps(request.payload, sort_keys=True).encode()
        
        # Generate HMAC-SHA256 signature
        signature = hmac.new(
            request.secret_key.encode(),
            payload_bytes,
            hashlib.sha256
        ).hexdigest()
        
        # Format as "sha256=hexdigest"
        full_signature = f"sha256={signature}"
        
        # Create example request
        example_request = {
            "url": "http://localhost:8000/ingest/{subscription_id}",
            "method": "POST",
            "headers": {
                "Content-Type": "application/json",
                "X-Hub-Signature-256": full_signature,
                "X-Event-Type": "user.created"  # Example event type
            },
            "body": request.payload
        }
        
        return SignatureResponse(
            signature=full_signature,
            headers={
                "X-Hub-Signature-256": full_signature
            },
            example_request=example_request
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error generating signature: {str(e)}") 