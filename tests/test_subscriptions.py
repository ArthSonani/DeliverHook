import pytest
from datetime import datetime
from app.models.models import Subscription

def test_create_subscription(client):
    """Test creating a new subscription."""
    response = client.post(
        "/subscriptions/",
        json={
            "target_url": "https://example.com/webhook",
            "secret_key": "test_secret_key",
            "event_types": ["order.created", "user.updated"]
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["target_url"] == "https://example.com/webhook"
    assert data["is_active"] is True
    assert data["event_types"] == ["order.created", "user.updated"]
    assert "id" in data

def test_get_subscription(client):
    """Test retrieving a subscription."""
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

    # Then get it
    response = client.get(f"/subscriptions/{subscription_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == subscription_id
    assert data["target_url"] == "https://example.com/webhook"
    assert data["secret_key"] is None  # Secret key should not be exposed

def test_update_subscription(client):
    """Test updating a subscription."""
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

    # Then update it
    response = client.put(
        f"/subscriptions/{subscription_id}",
        json={
            "target_url": "https://example.com/new-webhook",
            "secret_key": "new_secret_key",
            "event_types": ["order.created", "user.updated"]
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["target_url"] == "https://example.com/new-webhook"
    assert data["event_types"] == ["order.created", "user.updated"]

def test_delete_subscription(client):
    """Test deleting a subscription."""
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

    # Then delete it
    response = client.delete(f"/subscriptions/{subscription_id}")
    assert response.status_code == 200
    assert response.json()["message"] == "Subscription and associated delivery logs deleted successfully"

    # Verify it's deleted
    get_response = client.get(f"/subscriptions/{subscription_id}")
    assert get_response.status_code == 404 