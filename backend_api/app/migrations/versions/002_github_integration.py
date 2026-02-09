"""Add GitHub integration fields

Revision ID: 002
Revises: 001
Create Date: 2024-02-09 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '002'
down_revision: Union[str, None] = '001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add GitHub fields to users table
    op.add_column('users', sa.Column('github_username', sa.String(length=255), nullable=True))
    op.add_column('users', sa.Column('github_token', sa.Text(), nullable=True))
    op.add_column('users', sa.Column('github_token_expires_at', sa.DateTime(), nullable=True))
    op.add_column('users', sa.Column('github_account_linked', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('users', sa.Column('github_public_repos_count', sa.Integer(), nullable=False, server_default='0'))
    
    # Add GitHub fields to projects table
    op.add_column('projects', sa.Column('github_repo_url', sa.String(length=500), nullable=True))
    op.add_column('projects', sa.Column('github_repo_name', sa.String(length=255), nullable=True))
    op.add_column('projects', sa.Column('github_repo_id', sa.Integer(), nullable=True))
    op.add_column('projects', sa.Column('github_created_at', sa.DateTime(), nullable=True))
    op.add_column('projects', sa.Column('github_last_sync', sa.DateTime(), nullable=True))
    op.add_column('projects', sa.Column('github_topics', sa.Text(), nullable=True))
    op.add_column('projects', sa.Column('is_public', sa.Boolean(), nullable=False, server_default='false'))
    
    # Add GitHub fields to deployments table
    op.add_column('deployments', sa.Column('github_commit_sha', sa.String(length=40), nullable=True))
    op.add_column('deployments', sa.Column('github_pr_url', sa.String(length=500), nullable=True))
    op.add_column('deployments', sa.Column('github_release_tag', sa.String(length=255), nullable=True))


def downgrade() -> None:
    # Remove GitHub fields from deployments table
    op.drop_column('deployments', 'github_release_tag')
    op.drop_column('deployments', 'github_pr_url')
    op.drop_column('deployments', 'github_commit_sha')
    
    # Remove GitHub fields from projects table
    op.drop_column('projects', 'is_public')
    op.drop_column('projects', 'github_topics')
    op.drop_column('projects', 'github_last_sync')
    op.drop_column('projects', 'github_created_at')
    op.drop_column('projects', 'github_repo_id')
    op.drop_column('projects', 'github_repo_name')
    op.drop_column('projects', 'github_repo_url')
    
    # Remove GitHub fields from users table
    op.drop_column('users', 'github_public_repos_count')
    op.drop_column('users', 'github_account_linked')
    op.drop_column('users', 'github_token_expires_at')
    op.drop_column('users', 'github_token')
    op.drop_column('users', 'github_username')
