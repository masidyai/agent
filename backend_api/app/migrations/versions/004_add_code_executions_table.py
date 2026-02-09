"""Add code_executions table for Docker-based code execution

Revision ID: 004
Revises: 003
Create Date: 2026-02-09 03:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '004'
down_revision: Union[str, None] = '003'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create ENUM types if they don't exist
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE codeexecutionstatus AS ENUM (
                'PENDING', 'BUILDING', 'LINTING', 'TESTING', 'RUNNING', 
                'SUCCESS', 'FAILED', 'TIMEOUT', 'CANCELLED'
            );
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)
    
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE codeexecutionphase AS ENUM (
                'VALIDATION', 'BUILD', 'LINT', 'TEST', 'EXECUTION', 'CLEANUP'
            );
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)
    
    # Create code_executions table
    op.create_table(
        'code_executions',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('project_id', sa.UUID(), nullable=False),
        sa.Column('language', sa.String(length=50), nullable=True),
        sa.Column('command', sa.Text(), nullable=True),
        sa.Column('status', sa.Enum(
            'PENDING', 'BUILDING', 'LINTING', 'TESTING', 'RUNNING', 
            'SUCCESS', 'FAILED', 'TIMEOUT', 'CANCELLED',
            name='codeexecutionstatus',
            create_type=False
        ), nullable=False),
        sa.Column('current_phase', sa.Enum(
            'VALIDATION', 'BUILD', 'LINT', 'TEST', 'EXECUTION', 'CLEANUP',
            name='codeexecutionphase',
            create_type=False
        ), nullable=True),
        # Build phase
        sa.Column('build_status', sa.String(length=50), nullable=True),
        sa.Column('build_output', sa.Text(), nullable=True),
        sa.Column('build_error', sa.Text(), nullable=True),
        # Lint phase
        sa.Column('lint_status', sa.String(length=50), nullable=True),
        sa.Column('lint_output', sa.Text(), nullable=True),
        sa.Column('lint_issues', sa.JSON(), nullable=True),
        # Test phase
        sa.Column('test_status', sa.String(length=50), nullable=True),
        sa.Column('test_output', sa.Text(), nullable=True),
        sa.Column('tests_passed', sa.Integer(), nullable=True),
        sa.Column('tests_failed', sa.Integer(), nullable=True),
        sa.Column('test_coverage', sa.Float(), nullable=True),
        # Execution phase
        sa.Column('execution_output', sa.Text(), nullable=True),
        sa.Column('execution_error', sa.Text(), nullable=True),
        sa.Column('exit_code', sa.Integer(), nullable=True),
        # Validation & errors
        sa.Column('validation_errors', sa.JSON(), nullable=True),
        sa.Column('runtime_errors', sa.JSON(), nullable=True),
        # Performance metrics
        sa.Column('execution_time_ms', sa.Integer(), nullable=True),
        sa.Column('memory_used_mb', sa.Integer(), nullable=True),
        sa.Column('cpu_usage_percent', sa.Float(), nullable=True),
        # Docker container info
        sa.Column('container_id', sa.String(length=255), nullable=True),
        sa.Column('container_image', sa.String(length=255), nullable=True),
        # Timestamps
        sa.Column('started_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_code_executions_id'), 'code_executions', ['id'], unique=False)
    op.create_index(op.f('ix_code_executions_project_id'), 'code_executions', ['project_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_code_executions_project_id'), table_name='code_executions')
    op.drop_index(op.f('ix_code_executions_id'), table_name='code_executions')
    op.drop_table('code_executions')
    
    # Drop enums
    op.execute('DROP TYPE IF EXISTS codeexecutionstatus')
    op.execute('DROP TYPE IF EXISTS codeexecutionphase')
