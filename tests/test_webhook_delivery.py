import pytest
import hmac
import hashlib
import json
from datetime import datetime, timedelta
from app.models.models import Subscription, DeliveryLog

def test_webhook_ingestion(client):
    """Test webhook ingestion with valid signature."""
    # First create a subscription
    create_response = client.post(
        "/subscriptions/",
        json={
            "target_url": "https://example.com/webhook",
            "secret_key": "test_secret_key",
            "event_types": ["order.created"]
        }
    )
    subscription_id = create_response.json()["id"]

    # Prepare webhook payload
    payload = {"event": "order.created", "data": {"order_id": "123"}}
    payload_bytes = json.dumps(payload).encode()
    
    # Calculate signature
    signature = hmac.new(
        "test_secret_key".encode(),
        payload_bytes,
        hashlib.sha256
    ).hexdigest()

    # Send webhook
    response = client.post(
        f"/ingest/{subscription_id}",
        json=payload,
        headers={
            "X-Hub-Signature-256": f"sha256={signature}",
            "X-Event-Type": "order.created"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "webhook_id" in data
    assert data["message"] == "Webhook accepted for processing"

def test_webhook_delivery_status(client):
    """Test checking webhook delivery status."""
    # First create a subscription
    create_response = client.post(
        "/subscriptions/",
        json={
            "target_url": "https://example.com/webhook",
            "secret_key": "test_secret_key",
            "event_types": ["order.created"]
        }
    )
    subscription_id = create_response.json()["id"]

    # Send a webhook
    payload = {"event": "order.created", "data": {"order_id": "123"}}
    payload_bytes = json.dumps(payload).encode()
    signature = hmac.new(
        "test_secret_key".encode(),
        payload_bytes,
        hashlib.sha256
    ).hexdigest()

    ingest_response = client.post(
        f"/ingest/{subscription_id}",
        json=payload,
        headers={
            "X-Hub-Signature-256": f"sha256={signature}",
            "X-Event-Type": "order.created"
        }
    )
    webhook_id = ingest_response.json()["webhook_id"]

    # Check delivery status
    response = client.get(f"/status/{webhook_id}")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "attempts" in data
    assert data["attempts"] >= 0

def test_webhook_delivery_logs(client):
    """Test retrieving webhook delivery logs."""
    # First create a subscription
    create_response = client.post(
        "/subscriptions/",
        json={
            "target_url": "https://example.com/webhook",
            "secret_key": "test_secret_key",
            "event_types": ["order.created"]
        }
    )
    subscription_id = create_response.json()["id"]

    # Send multiple webhooks
    for i in range(3):
        payload = {"event": "order.created", "data": {"order_id": f"123{i}"}}
        payload_bytes = json.dumps(payload).encode()
        signature = hmac.new(
            "test_secret_key".encode(),
            payload_bytes,
            hashlib.sha256
        ).hexdigest()

        client.post(
            f"/ingest/{subscription_id}",
            json=payload,
            headers={
                "X-Hub-Signature-256": f"sha256={signature}",
                "X-Event-Type": "order.created"
            }
        )

    # Get delivery logs
    response = client.get(f"/logs/{subscription_id}")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 3  # Should have at least 3 delivery logs

def test_webhook_retry_mechanism(client):
    """Test webhook retry mechanism."""
    # Create a subscription with a failing target URL
    create_response = client.post(
        "/subscriptions/",
        json={
            "target_url": "https://example.com/failing-webhook",
            "secret_key": "test_secret_key",
            "event_types": ["order.created"]
        }
    )
    subscription_id = create_response.json()["id"]

    # Send a webhook
    payload = {"event": "order.created", "data": {"order_id": "123"}}
    payload_bytes = json.dumps(payload).encode()
    signature = hmac.new(
        "test_secret_key".encode(),
        payload_bytes,
        hashlib.sha256
    ).hexdigest()

    ingest_response = client.post(
        f"/ingest/{subscription_id}",
        json=payload,
        headers={
            "X-Hub-Signature-256": f"sha256={signature}",
            "X-Event-Type": "order.created"
        }
    )
    webhook_id = ingest_response.json()["webhook_id"]

    # Check status after a short delay
    response = client.get(f"/status/{webhook_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ["pending", "failed"]
    assert data["attempts"] > 0 