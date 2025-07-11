import httpx
import hmac
import hashlib
import json
from datetime import datetime, timedelta
from celery import shared_task
from app.core.config import settings
from app.db.session import SessionLocal
from app.models.models import Subscription, DeliveryLog
from celery.exceptions import MaxRetriesExceededError

@shared_task(bind=True, max_retries=settings.MAX_RETRY_ATTEMPTS)
def deliver_webhook(self, subscription_id: int, webhook_id: str, payload: dict, event_type: str = None):
    db = SessionLocal()
    try:
        # Get subscription details
        subscription = db.query(Subscription).filter(
            Subscription.id == subscription_id,
            Subscription.is_active == True
        ).first()
        
        if not subscription:
            raise ValueError(f"Subscription {subscription_id} not found or inactive")

        # Create signature if secret key exists
        headers = {}
        if subscription.secret_key:
            signature = hmac.new(
                subscription.secret_key.encode(),
                json.dumps(payload).encode(),
                hashlib.sha256
            ).hexdigest()
            headers["X-Webhook-Signature"] = signature
        
        # Add event type header if present
        if event_type:
            headers["X-Event-Type"] = event_type

        # Attempt delivery
        try:
            with httpx.Client(timeout=10.0) as client:
                response = client.post(
                    subscription.target_url,
                    json=payload,
                    headers=headers
                )
                
                # Log the attempt
                log = DeliveryLog(
                    subscription_id=subscription_id,
                    webhook_id=webhook_id,
                    event_type=event_type,
                    payload=payload,
                    attempt_number=self.request.retries + 1,
                    status_code=response.status_code,
                    response_body=response.text,
                    is_success=200 <= response.status_code < 300
                )
                db.add(log)
                db.commit()

                # If successful, we're done
                if log.is_success:
                    return True

                # If not successful, raise exception to trigger retry
                raise Exception(f"Delivery failed with status code {response.status_code}")

        except Exception as e:
            # Log the failed attempt
            log = DeliveryLog(
                subscription_id=subscription_id,
                webhook_id=webhook_id,
                event_type=event_type,
                payload=payload,
                attempt_number=self.request.retries + 1,
                error_message=str(e),
                is_success=False
            )
            db.add(log)
            db.commit()

            # Calculate retry delay with exponential backoff
            retry_delay = 10 * (2 ** self.request.retries)  # 10s, 20s, 40s, etc.
            
            try:
                self.retry(exc=e, countdown=retry_delay)
            except MaxRetriesExceededError:
                return False

    finally:
        db.close()

@shared_task
def cleanup_old_logs():
    """Clean up delivery logs older than the retention period"""
    db = SessionLocal()
    try:
        retention_period = datetime.utcnow() - timedelta(hours=settings.LOG_RETENTION_HOURS)
        db.query(DeliveryLog).filter(DeliveryLog.created_at < retention_period).delete()
        db.commit()
    finally:
        db.close() 