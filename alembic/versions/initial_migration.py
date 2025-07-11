"""initial migration

Revision ID: initial
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'initial'
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Create subscriptions table
    op.create_table(
        'subscriptions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('target_url', sa.String(), nullable=False),
        sa.Column('secret_key', sa.String(), nullable=True),
        sa.Column('event_types', sa.ARRAY(sa.String()), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create delivery_logs table
    op.create_table(
        'delivery_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('subscription_id', sa.Integer(), nullable=False),
        sa.Column('webhook_id', sa.String(), nullable=False),
        sa.Column('event_type', sa.String(), nullable=True),
        sa.Column('payload', sa.JSON(), nullable=False),
        sa.Column('attempt_number', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('status_code', sa.Integer(), nullable=True),
        sa.Column('response_body', sa.String(), nullable=True),
        sa.Column('error_message', sa.String(), nullable=True),
        sa.Column('is_success', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['subscription_id'], ['subscriptions.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes
    op.create_index('ix_subscriptions_id', 'subscriptions', ['id'])
    op.create_index('ix_delivery_logs_id', 'delivery_logs', ['id'])
    op.create_index('ix_delivery_logs_webhook_id', 'delivery_logs', ['webhook_id'])
    op.create_index('ix_delivery_logs_subscription_id', 'delivery_logs', ['subscription_id'])

def downgrade() -> None:
    op.drop_table('delivery_logs')
    op.drop_table('subscriptions') 