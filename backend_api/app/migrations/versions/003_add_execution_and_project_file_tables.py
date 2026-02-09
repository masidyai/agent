"""add execution and project file tables

Revision ID: 003
Revises: 002
Create Date: 2026-02-09 01:10:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '003'
down_revision: Union[str, None] = '002'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add execution and project_file tables"""
    # Create ENUM types if they don't exist
    # PostgreSQL doesn't support CREATE TYPE IF NOT EXISTS before version 9.1
    # So we use a function to check and create
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE executionstatus AS ENUM ('pending', 'in_progress', 'completed', 'failed', 'stopped');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)
    
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE stepstatus AS ENUM ('pending', 'in_progress', 'completed', 'failed', 'skipped');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)
    
    # Create executions table
    op.create_table(
        'executions',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('project_id', sa.Uuid(), nullable=False),
        sa.Column('prompt', sa.Text(), nullable=True),
        sa.Column('plan', sa.Text(), nullable=True),
        sa.Column('status', sa.String(), nullable=False),
        sa.Column('started_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_executions_id'), 'executions', ['id'], unique=False)
    op.create_index(op.f('ix_executions_project_id'), 'executions', ['project_id'], unique=False)
    
    # Alter the status column to use the ENUM type
    # Handle potential case conversion for existing data
    op.execute("""
        ALTER TABLE executions 
        ALTER COLUMN status TYPE executionstatus 
        USING CASE 
            WHEN UPPER(status) = 'PENDING' THEN 'pending'::executionstatus
            WHEN UPPER(status) = 'IN_PROGRESS' THEN 'in_progress'::executionstatus
            WHEN UPPER(status) = 'COMPLETED' THEN 'completed'::executionstatus
            WHEN UPPER(status) = 'FAILED' THEN 'failed'::executionstatus
            WHEN UPPER(status) = 'STOPPED' THEN 'stopped'::executionstatus
            ELSE status::executionstatus
        END
    """)
    
    # Create project_files table
    op.create_table(
        'project_files',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('project_id', sa.Uuid(), nullable=False),
        sa.Column('file_path', sa.String(length=500), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('language', sa.String(length=50), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_project_files_id'), 'project_files', ['id'], unique=False)
    op.create_index(op.f('ix_project_files_project_id'), 'project_files', ['project_id'], unique=False)
    
    # Create execution_steps table
    op.create_table(
        'execution_steps',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('execution_id', sa.Uuid(), nullable=False),
        sa.Column('step_number', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('tool_name', sa.String(length=100), nullable=True),
        sa.Column('status', sa.String(), nullable=False),
        sa.Column('output', sa.Text(), nullable=True),
        sa.Column('logs', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['execution_id'], ['executions.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_execution_steps_execution_id'), 'execution_steps', ['execution_id'], unique=False)
    op.create_index(op.f('ix_execution_steps_id'), 'execution_steps', ['id'], unique=False)
    
    # Alter the status column to use the ENUM type
    # Handle potential case conversion for existing data
    op.execute("""
        ALTER TABLE execution_steps 
        ALTER COLUMN status TYPE stepstatus 
        USING CASE 
            WHEN UPPER(status) = 'PENDING' THEN 'pending'::stepstatus
            WHEN UPPER(status) = 'IN_PROGRESS' THEN 'in_progress'::stepstatus
            WHEN UPPER(status) = 'COMPLETED' THEN 'completed'::stepstatus
            WHEN UPPER(status) = 'FAILED' THEN 'failed'::stepstatus
            WHEN UPPER(status) = 'SKIPPED' THEN 'skipped'::stepstatus
            ELSE status::stepstatus
        END
    """)


def downgrade() -> None:
    """Remove execution and project_file tables"""
    op.drop_index(op.f('ix_execution_steps_id'), table_name='execution_steps')
    op.drop_index(op.f('ix_execution_steps_execution_id'), table_name='execution_steps')
    op.drop_table('execution_steps')
    op.drop_index(op.f('ix_project_files_project_id'), table_name='project_files')
    op.drop_index(op.f('ix_project_files_id'), table_name='project_files')
    op.drop_table('project_files')
    op.drop_index(op.f('ix_executions_project_id'), table_name='executions')
    op.drop_index(op.f('ix_executions_id'), table_name='executions')
    op.drop_table('executions')
    
    # Drop enums
    op.execute('DROP TYPE IF EXISTS executionstatus')
    op.execute('DROP TYPE IF EXISTS stepstatus')
