"""Add performance indexes

Revision ID: 004
Revises: 003
Create Date: 2024-12-27

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '004'
down_revision = '003'
branch_labels = None
depends_on = None


def upgrade():
    # Index on beneficiary_data for common queries
    op.create_index(
        'idx_beneficiary_data_program_date',
        'beneficiary_data',
        ['program_id', 'reference_date'],
        unique=False
    )
    
    op.create_index(
        'idx_beneficiary_data_municipality',
        'beneficiary_data',
        ['municipality_id'],
        unique=False
    )
    
    # Index on municipalities for search
    op.create_index(
        'idx_municipalities_name',
        'municipalities',
        ['name'],
        unique=False
    )
    
    op.create_index(
        'idx_municipalities_state',
        'municipalities',
        ['state_id'],
        unique=False
    )
    
    # Index on programs for active filtering
    op.create_index(
        'idx_programs_active',
        'programs',
        ['is_active'],
        unique=False
    )
    
    # GIST index for PostGIS geometry (if not already exists)
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_municipalities_geometry 
        ON municipalities USING GIST (geometry);
    """)


def downgrade():
    op.drop_index('idx_beneficiary_data_program_date', table_name='beneficiary_data')
    op.drop_index('idx_beneficiary_data_municipality', table_name='beneficiary_data')
    op.drop_index('idx_municipalities_name', table_name='municipalities')
    op.drop_index('idx_municipalities_state', table_name='municipalities')
    op.drop_index('idx_programs_active', table_name='programs')
    op.execute("DROP INDEX IF EXISTS idx_municipalities_geometry;")






