"""Add chain events table

Revision ID: 006
Revises: 005
Create Date: 2026-02-09 08:10:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '006'
down_revision: Union[str, None] = '005'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create chain_events table
    op.create_table(
        'chain_events',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('event_id', sa.String(length=100), nullable=False),
        sa.Column('actor', sa.String(length=255), nullable=False),
        sa.Column('actor_type', sa.String(length=50), nullable=False),
        sa.Column('action', sa.String(length=255), nullable=False),
        sa.Column('target', sa.String(length=255), nullable=True),
        sa.Column('target_type', sa.String(length=50), nullable=True),
        sa.Column('ai_risk_score', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('risk_level', sa.String(length=20), nullable=False, server_default='low'),
        sa.Column('event_hash', sa.String(length=64), nullable=False),
        sa.Column('prev_hash', sa.String(length=64), nullable=True),
        sa.Column('metadata', sa.Text(), nullable=True),
        sa.Column('ip_address', sa.String(length=50), nullable=True),
        sa.Column('user_agent', sa.String(length=500), nullable=True),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_chain_events_id'), 'chain_events', ['id'], unique=False)
    op.create_index(op.f('ix_chain_events_event_id'), 'chain_events', ['event_id'], unique=True)
    op.create_index(op.f('ix_chain_events_actor'), 'chain_events', ['actor'], unique=False)
    op.create_index(op.f('ix_chain_events_action'), 'chain_events', ['action'], unique=False)
    op.create_index(op.f('ix_chain_events_ai_risk_score'), 'chain_events', ['ai_risk_score'], unique=False)
    op.create_index(op.f('ix_chain_events_event_hash'), 'chain_events', ['event_hash'], unique=False)
    op.create_index(op.f('ix_chain_events_timestamp'), 'chain_events', ['timestamp'], unique=False)
    op.create_index('ix_chain_events_actor_timestamp', 'chain_events', ['actor', 'timestamp'], unique=False)
    op.create_index('ix_chain_events_action_timestamp', 'chain_events', ['action', 'timestamp'], unique=False)


def downgrade() -> None:
    op.drop_index('ix_chain_events_action_timestamp', table_name='chain_events')
    op.drop_index('ix_chain_events_actor_timestamp', table_name='chain_events')
    op.drop_index(op.f('ix_chain_events_timestamp'), table_name='chain_events')
    op.drop_index(op.f('ix_chain_events_event_hash'), table_name='chain_events')
    op.drop_index(op.f('ix_chain_events_ai_risk_score'), table_name='chain_events')
    op.drop_index(op.f('ix_chain_events_action'), table_name='chain_events')
    op.drop_index(op.f('ix_chain_events_actor'), table_name='chain_events')
    op.drop_index(op.f('ix_chain_events_event_id'), table_name='chain_events')
    op.drop_index(op.f('ix_chain_events_id'), table_name='chain_events')
    op.drop_table('chain_events')
