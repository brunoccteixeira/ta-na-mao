"""Initial schema with PostGIS

Revision ID: 001
Revises:
Create Date: 2024-12-19

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import geoalchemy2


revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Enable PostGIS
    op.execute('CREATE EXTENSION IF NOT EXISTS postgis')

    # States table
    op.create_table(
        'states',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('ibge_code', sa.String(2), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('abbreviation', sa.String(2), nullable=False),
        sa.Column('region', sa.String(20), nullable=False),
        sa.Column('geometry', geoalchemy2.Geometry('MULTIPOLYGON', srid=4326), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_states_ibge_code', 'states', ['ibge_code'], unique=True)
    op.create_index('ix_states_abbreviation', 'states', ['abbreviation'])
    op.create_index('ix_states_region', 'states', ['region'])

    # Municipalities table
    op.create_table(
        'municipalities',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('ibge_code', sa.String(7), nullable=False),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('state_id', sa.Integer(), nullable=False),
        sa.Column('population', sa.Integer(), nullable=True),
        sa.Column('area_km2', sa.Numeric(12, 2), nullable=True),
        sa.Column('geometry', geoalchemy2.Geometry('MULTIPOLYGON', srid=4326), nullable=True),
        sa.Column('geometry_simplified', geoalchemy2.Geometry('MULTIPOLYGON', srid=4326), nullable=True),
        sa.Column('centroid', geoalchemy2.Geometry('POINT', srid=4326), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['state_id'], ['states.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_municipalities_ibge_code', 'municipalities', ['ibge_code'], unique=True)
    op.create_index('ix_municipalities_state_id', 'municipalities', ['state_id'])

    # Programs table
    op.create_table(
        'programs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('code', sa.String(50), nullable=False),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('description', sa.String(1000), nullable=True),
        sa.Column('data_source_url', sa.String(500), nullable=True),
        sa.Column('update_frequency', sa.String(50), nullable=True),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_programs_code', 'programs', ['code'], unique=True)

    # Beneficiary data table
    op.create_table(
        'beneficiary_data',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('municipality_id', sa.Integer(), nullable=False),
        sa.Column('program_id', sa.Integer(), nullable=False),
        sa.Column('reference_date', sa.Date(), nullable=False),
        sa.Column('total_beneficiaries', sa.Integer(), nullable=True),
        sa.Column('total_families', sa.Integer(), nullable=True),
        sa.Column('total_value_brl', sa.Numeric(15, 2), nullable=True),
        sa.Column('coverage_rate', sa.Numeric(5, 4), nullable=True),
        sa.Column('extra_data', sa.JSON(), nullable=True),
        sa.Column('data_source', sa.String(100), nullable=True),
        sa.Column('ingested_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['municipality_id'], ['municipalities.id']),
        sa.ForeignKeyConstraint(['program_id'], ['programs.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('municipality_id', 'program_id', 'reference_date'),
    )
    op.create_index('ix_beneficiary_data_municipality_id', 'beneficiary_data', ['municipality_id'])
    op.create_index('ix_beneficiary_data_program_id', 'beneficiary_data', ['program_id'])
    op.create_index('ix_beneficiary_data_reference_date', 'beneficiary_data', ['reference_date'])

    # CadÚnico data table
    op.create_table(
        'cadunico_data',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('municipality_id', sa.Integer(), nullable=False),
        sa.Column('reference_date', sa.Date(), nullable=False),
        sa.Column('total_families', sa.Integer(), nullable=True),
        sa.Column('total_persons', sa.Integer(), nullable=True),
        sa.Column('families_extreme_poverty', sa.Integer(), nullable=True),
        sa.Column('families_poverty', sa.Integer(), nullable=True),
        sa.Column('families_low_income', sa.Integer(), nullable=True),
        sa.Column('persons_0_5_years', sa.Integer(), nullable=True),
        sa.Column('persons_6_14_years', sa.Integer(), nullable=True),
        sa.Column('persons_15_17_years', sa.Integer(), nullable=True),
        sa.Column('persons_18_64_years', sa.Integer(), nullable=True),
        sa.Column('persons_65_plus', sa.Integer(), nullable=True),
        sa.Column('ingested_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['municipality_id'], ['municipalities.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('municipality_id', 'reference_date'),
    )
    op.create_index('ix_cadunico_data_municipality_id', 'cadunico_data', ['municipality_id'])
    op.create_index('ix_cadunico_data_reference_date', 'cadunico_data', ['reference_date'])


def downgrade() -> None:
    op.drop_table('cadunico_data')
    op.drop_table('beneficiary_data')
    op.drop_table('programs')
    op.drop_table('municipalities')
    op.drop_table('states')
