"""add cras_locations table

Revision ID: 006
Revises: 005
Create Date: 2026-02-05

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, ARRAY

# revision identifiers, used by Alembic.
revision = '006'
down_revision = '005'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'cras_locations',
        sa.Column('id', UUID(as_uuid=True), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('ibge_code', sa.String(7), sa.ForeignKey('municipalities.ibge_code'), nullable=False),
        sa.Column('nome', sa.String(255), nullable=False),
        sa.Column('endereco', sa.String(500), nullable=True),
        sa.Column('bairro', sa.String(100), nullable=True),
        sa.Column('cep', sa.String(8), nullable=True),
        sa.Column('telefone', sa.String(20), nullable=True),
        sa.Column('email', sa.String(255), nullable=True),
        sa.Column('latitude', sa.Float(), nullable=True),
        sa.Column('longitude', sa.Float(), nullable=True),
        sa.Column('servicos', ARRAY(sa.String), nullable=True),  # ["CadUnico", "BolsaFamilia", "BPC"]
        sa.Column('horario_funcionamento', sa.String(100), nullable=True),
        sa.Column('source', sa.String(50), nullable=True),  # "censo_suas", "mapa_social"
        sa.Column('geocode_source', sa.String(50), nullable=True),  # "cnefe", "google", "manual"
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
    )

    # Index for IBGE code lookups
    op.create_index('ix_cras_locations_ibge_code', 'cras_locations', ['ibge_code'], unique=False)

    # Spatial index for coordinate-based queries
    op.create_index('ix_cras_locations_coords', 'cras_locations', ['latitude', 'longitude'], unique=False)

    # Index for source filtering
    op.create_index('ix_cras_locations_source', 'cras_locations', ['source'], unique=False)


def downgrade() -> None:
    op.drop_index('ix_cras_locations_source', table_name='cras_locations')
    op.drop_index('ix_cras_locations_coords', table_name='cras_locations')
    op.drop_index('ix_cras_locations_ibge_code', table_name='cras_locations')
    op.drop_table('cras_locations')
