"""Add chain identity tables

Revision ID: 005
Revises: 004
Create Date: 2026-02-09 08:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '005'
down_revision: Union[str, None] = '004'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create key status ENUM type
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE keystatus AS ENUM ('active', 'rotated', 'revoked');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)
    
    # Create masidy_identities table
    op.create_table(
        'masidy_identities',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('masidy_id', sa.String(length=100), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('root_key_id', sa.UUID(), nullable=True),
        sa.Column('device_fingerprint', sa.String(length=500), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_masidy_identities_id'), 'masidy_identities', ['id'], unique=False)
    op.create_index(op.f('ix_masidy_identities_masidy_id'), 'masidy_identities', ['masidy_id'], unique=True)
    op.create_index(op.f('ix_masidy_identities_user_id'), 'masidy_identities', ['user_id'], unique=True)
    op.create_index(op.f('ix_masidy_identities_created_at'), 'masidy_identities', ['created_at'], unique=False)
    
    # Create root_keys table
    op.create_table(
        'root_keys',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('key_id', sa.String(length=100), nullable=False),
        sa.Column('masidy_id', sa.String(length=100), nullable=False),
        sa.Column('encrypted_key', sa.Text(), nullable=False),
        sa.Column('status', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('rotated_at', sa.DateTime(), nullable=True),
        sa.Column('revoked_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['masidy_id'], ['masidy_identities.masidy_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_root_keys_id'), 'root_keys', ['id'], unique=False)
    op.create_index(op.f('ix_root_keys_key_id'), 'root_keys', ['key_id'], unique=True)
    op.create_index(op.f('ix_root_keys_masidy_id'), 'root_keys', ['masidy_id'], unique=False)
    op.create_index(op.f('ix_root_keys_status'), 'root_keys', ['status'], unique=False)
    op.create_index(op.f('ix_root_keys_created_at'), 'root_keys', ['created_at'], unique=False)
    op.create_index('ix_root_keys_masidy_status', 'root_keys', ['masidy_id', 'status'], unique=False)
    
    # Alter status column to use ENUM
    op.execute("""
        ALTER TABLE root_keys 
        ALTER COLUMN status TYPE keystatus 
        USING status::keystatus
    """)
    
    # Create derived_keys table
    op.create_table(
        'derived_keys',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('key_id', sa.String(length=100), nullable=False),
        sa.Column('masidy_id', sa.String(length=100), nullable=False),
        sa.Column('scope', sa.String(length=255), nullable=False),
        sa.Column('scope_id', sa.String(length=100), nullable=True),
        sa.Column('encrypted_key', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('last_used_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['masidy_id'], ['masidy_identities.masidy_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_derived_keys_id'), 'derived_keys', ['id'], unique=False)
    op.create_index(op.f('ix_derived_keys_key_id'), 'derived_keys', ['key_id'], unique=True)
    op.create_index(op.f('ix_derived_keys_masidy_id'), 'derived_keys', ['masidy_id'], unique=False)
    op.create_index(op.f('ix_derived_keys_scope'), 'derived_keys', ['scope'], unique=False)
    op.create_index(op.f('ix_derived_keys_created_at'), 'derived_keys', ['created_at'], unique=False)
    op.create_index('ix_derived_keys_masidy_scope', 'derived_keys', ['masidy_id', 'scope'], unique=False)


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_index('ix_derived_keys_masidy_scope', table_name='derived_keys')
    op.drop_index(op.f('ix_derived_keys_created_at'), table_name='derived_keys')
    op.drop_index(op.f('ix_derived_keys_scope'), table_name='derived_keys')
    op.drop_index(op.f('ix_derived_keys_masidy_id'), table_name='derived_keys')
    op.drop_index(op.f('ix_derived_keys_key_id'), table_name='derived_keys')
    op.drop_index(op.f('ix_derived_keys_id'), table_name='derived_keys')
    op.drop_table('derived_keys')
    
    op.drop_index('ix_root_keys_masidy_status', table_name='root_keys')
    op.drop_index(op.f('ix_root_keys_created_at'), table_name='root_keys')
    op.drop_index(op.f('ix_root_keys_status'), table_name='root_keys')
    op.drop_index(op.f('ix_root_keys_masidy_id'), table_name='root_keys')
    op.drop_index(op.f('ix_root_keys_key_id'), table_name='root_keys')
    op.drop_index(op.f('ix_root_keys_id'), table_name='root_keys')
    op.drop_table('root_keys')
    
    op.drop_index(op.f('ix_masidy_identities_created_at'), table_name='masidy_identities')
    op.drop_index(op.f('ix_masidy_identities_user_id'), table_name='masidy_identities')
    op.drop_index(op.f('ix_masidy_identities_masidy_id'), table_name='masidy_identities')
    op.drop_index(op.f('ix_masidy_identities_id'), table_name='masidy_identities')
    op.drop_table('masidy_identities')
    
    # Drop ENUM type
    op.execute('DROP TYPE IF EXISTS keystatus')
