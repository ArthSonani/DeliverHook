from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
import uuid
import hmac
import hashlib
import json
from typing import Optional
from app.db.session import get_db
from app.models.models import Subscription, DeliveryLog
from app.tasks.delivery_tasks import deliver_webhook
from app.core.cache import get_cache, Cache
from app.core.security import decrypt_secret

router = APIRouter()

def verify_signature(payload: bytes, signature: str, encrypted_secret: str) -> bool:
    if not encrypted_secret or not signature:
        return False
    
    try:
        # Decrypt the secret key
        secret_key = decrypt_secret(encrypted_secret)
        
        # Remove 'sha256=' prefix if present
        provided_signature = signature.split('=')[1] if '=' in signature else signature
        
        # Calculate the expected signature
        expected_signature = hmac.new(
            secret_key.encode(),
            payload,
            hashlib.sha256
        ).hexdigest()
        
        # Compare the signatures
        return hmac.compare_digest(provided_signature, expected_signature)
    except Exception:
        return False

@router.post("/{subscription_id}")
async def ingest_webhook(
    subscription_id: int,
    payload: dict,
    db: Session = Depends(get_db),
    cache: Cache = Depends(get_cache),
    x_hub_signature_256: Optional[str] = Header(None),
    x_event_type: Optional[str] = Header(None)
):
    # Check if subscription exists and is active
    subscription = db.query(Subscription).filter(
        Subscription.id == subscription_id,
        Subscription.is_active == True
    ).first()
    
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found or inactive")
    
    # Verify signature if secret key exists
    if subscription.secret_key:
        if not x_hub_signature_256:
            raise HTTPException(
                status_code=400,
                detail="Missing X-Hub-Signature-256 header"
            )
        
        # Convert payload to bytes for signature verification
        payload_bytes = json.dumps(payload, sort_keys=True).encode()
        
        if not verify_signature(payload_bytes, x_hub_signature_256, subscription.secret_key):
            raise HTTPException(
                status_code=401,
                detail="Invalid signature"
            )
    
    # Check event type filtering
    if subscription.event_types and x_event_type:
        if x_event_type not in subscription.event_types:
            raise HTTPException(
                status_code=400,
                detail=f"Event type {x_event_type} not allowed for this subscription"
            )
    
    # Generate a unique webhook ID
    webhook_id = str(uuid.uuid4())
    
    # Queue the delivery task
    deliver_webhook.delay(subscription_id, webhook_id, payload, x_event_type)
    
    return {
        "message": "Webhook accepted for processing",
        "webhook_id": webhook_id
    } 