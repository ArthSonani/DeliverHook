from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, Boolean, ARRAY, Index
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    target_url = Column(String, nullable=False)
    secret_key = Column(String, nullable=True)
    event_types = Column(ARRAY(String), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    __table_args__ = (
        Index('idx_subscriptions_is_active', 'is_active'),
        Index('idx_subscriptions_created_at', 'created_at'),
    )

class DeliveryLog(Base):
    __tablename__ = "delivery_logs"

    id = Column(Integer, primary_key=True, index=True)
    subscription_id = Column(Integer, ForeignKey("subscriptions.id"))
    webhook_id = Column(String, index=True)
    event_type = Column(String, nullable=True)  # Store the event type
    payload = Column(JSON)
    attempt_number = Column(Integer, default=1)
    status_code = Column(Integer, nullable=True)
    response_body = Column(String, nullable=True)
    error_message = Column(String, nullable=True)
    is_success = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Add indexes for frequently queried columns
    __table_args__ = (
        Index('idx_delivery_logs_subscription_id', 'subscription_id'),
        Index('idx_delivery_logs_webhook_id', 'webhook_id'),
        Index('idx_delivery_logs_created_at', 'created_at'),
        Index('idx_delivery_logs_is_success', 'is_success'),
        Index('idx_delivery_logs_event_type', 'event_type'),

    ) 

