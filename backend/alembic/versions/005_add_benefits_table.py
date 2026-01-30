"""add benefits table

Revision ID: 005
Revises: 004
Create Date: 2026-01-29

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB, ARRAY

# revision identifiers, used by Alembic.
revision = '005'
down_revision = '004'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'benefits',
        sa.Column('id', sa.String(100), nullable=False),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('short_description', sa.Text(), nullable=False),

        # Scope
        sa.Column('scope', sa.String(20), nullable=False),  # federal, state, municipal, sectoral
        sa.Column('state', sa.String(2), nullable=True),  # UF code
        sa.Column('municipality_ibge', sa.String(7), nullable=True),  # IBGE code
        sa.Column('sector', sa.String(50), nullable=True),  # pescador, agricultor, etc.

        # Value
        sa.Column('estimated_value', JSONB(astext_type=sa.Text()), nullable=True),

        # Eligibility
        sa.Column('eligibility_rules', JSONB(astext_type=sa.Text()), nullable=False),

        # Practical info
        sa.Column('where_to_apply', sa.Text(), nullable=False),
        sa.Column('documents_required', ARRAY(sa.String), nullable=False),
        sa.Column('how_to_apply', ARRAY(sa.String), nullable=True),

        # Metadata
        sa.Column('source_url', sa.String(500), nullable=True),
        sa.Column('last_updated', sa.Date(), nullable=False),
        sa.Column('status', sa.String(20), nullable=False, default='active'),

        # UI
        sa.Column('icon', sa.String(10), nullable=True),
        sa.Column('category', sa.String(100), nullable=True),

        # Timestamps
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),

        sa.PrimaryKeyConstraint('id'),
    )

    # Indices for common queries
    op.create_index('ix_benefits_scope', 'benefits', ['scope'], unique=False)
    op.create_index('ix_benefits_state', 'benefits', ['state'], unique=False)
    op.create_index('ix_benefits_municipality_ibge', 'benefits', ['municipality_ibge'], unique=False)
    op.create_index('ix_benefits_sector', 'benefits', ['sector'], unique=False)
    op.create_index('ix_benefits_status', 'benefits', ['status'], unique=False)
    op.create_index('ix_benefits_category', 'benefits', ['category'], unique=False)

    # Composite index for location-based queries
    op.create_index(
        'ix_benefits_location',
        'benefits',
        ['scope', 'state', 'municipality_ibge'],
        unique=False
    )


def downgrade() -> None:
    op.drop_index('ix_benefits_location', table_name='benefits')
    op.drop_index('ix_benefits_category', table_name='benefits')
    op.drop_index('ix_benefits_status', table_name='benefits')
    op.drop_index('ix_benefits_sector', table_name='benefits')
    op.drop_index('ix_benefits_municipality_ibge', table_name='benefits')
    op.drop_index('ix_benefits_state', table_name='benefits')
    op.drop_index('ix_benefits_scope', table_name='benefits')
    op.drop_table('benefits')
