"""Initial schema — users, widgets, submissions

Revision ID: 001_initial
Revises: None
Create Date: 2026-08-30

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001_initial'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Users table
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('email', sa.String(255), nullable=False, unique=True),
        sa.Column('hashed_password', sa.String(255), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.now()),
    )
    op.create_index('ix_users_email', 'users', ['email'])

    # Widgets table
    op.create_table(
        'widgets',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('owner_id', postgresql.UUID(as_uuid=True),
                  sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('widget_type', sa.Enum('signup_form', 'contact_form', 'cta_popover',
                                         name='widgettype'), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('form_fields', postgresql.JSON, nullable=False, server_default='[]'),
        sa.Column('button_text', sa.String(100), nullable=False, server_default='Submit'),
        sa.Column('display_options', postgresql.JSON, nullable=False, server_default='{}'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.now()),
    )
    op.create_index('ix_widgets_owner_id', 'widgets', ['owner_id'])

    # Submissions table
    op.create_table(
        'submissions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('widget_id', postgresql.UUID(as_uuid=True),
                  sa.ForeignKey('widgets.id', ondelete='CASCADE'), nullable=False),
        sa.Column('idempotency_key', sa.String(255), nullable=True, unique=True),
        sa.Column('data', postgresql.JSON, nullable=False),
        sa.Column('ip_address', sa.String(45), nullable=True),
        sa.Column('user_agent', sa.Text, nullable=True),
        sa.Column('geo_country', sa.String(100), nullable=True),
        sa.Column('geo_city', sa.String(100), nullable=True),
        sa.Column('geo_region', sa.String(100), nullable=True),
        sa.Column('geo_lat', sa.Float, nullable=True),
        sa.Column('geo_lon', sa.Float, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.now()),
    )
    op.create_index('ix_submissions_widget_id', 'submissions', ['widget_id'])
    op.create_index('ix_submissions_idempotency_key', 'submissions', ['idempotency_key'])
    op.create_index('ix_submissions_created_at', 'submissions', ['created_at'])


def downgrade() -> None:
    op.drop_table('submissions')
    op.drop_table('widgets')
    op.drop_table('users')
    op.execute("DROP TYPE IF EXISTS widgettype")
