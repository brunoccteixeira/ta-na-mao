"""add beneficiarios table

Revision ID: 003
Revises: 002
Create Date: 2024-12-26

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'beneficiarios',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('cpf_hash', sa.String(64), nullable=False),
        sa.Column('cpf_masked', sa.String(14), nullable=True),
        sa.Column('nis', sa.String(11), nullable=True),
        sa.Column('nome', sa.String(200), nullable=True),
        sa.Column('ibge_code', sa.String(7), nullable=True),
        sa.Column('uf', sa.String(2), nullable=True),
        # Bolsa Familia
        sa.Column('bf_ativo', sa.Boolean(), default=False, nullable=True),
        sa.Column('bf_valor', sa.Numeric(10, 2), nullable=True),
        sa.Column('bf_parcela_mes', sa.String(7), nullable=True),
        sa.Column('bf_data_referencia', sa.Date(), nullable=True),
        # BPC
        sa.Column('bpc_ativo', sa.Boolean(), default=False, nullable=True),
        sa.Column('bpc_valor', sa.Numeric(10, 2), nullable=True),
        sa.Column('bpc_tipo', sa.String(20), nullable=True),
        sa.Column('bpc_data_referencia', sa.Date(), nullable=True),
        # CadUnico
        sa.Column('cadunico_ativo', sa.Boolean(), default=False, nullable=True),
        sa.Column('cadunico_data_atualizacao', sa.Date(), nullable=True),
        sa.Column('cadunico_faixa_renda', sa.String(50), nullable=True),
        # Metadata
        sa.Column('criado_em', sa.DateTime(), nullable=True),
        sa.Column('atualizado_em', sa.DateTime(), nullable=True),
        sa.Column('fonte', sa.String(50), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['ibge_code'], ['municipalities.ibge_code']),
        sa.UniqueConstraint('cpf_hash')
    )
    # Indices
    op.create_index('ix_beneficiarios_cpf_hash', 'beneficiarios', ['cpf_hash'], unique=True)
    op.create_index('ix_beneficiarios_nis', 'beneficiarios', ['nis'], unique=False)
    op.create_index('ix_beneficiarios_ibge', 'beneficiarios', ['ibge_code'], unique=False)
    op.create_index('ix_beneficiarios_bf_ativo', 'beneficiarios', ['bf_ativo'], unique=False)
    op.create_index('ix_beneficiarios_bpc_ativo', 'beneficiarios', ['bpc_ativo'], unique=False)


def downgrade() -> None:
    op.drop_index('ix_beneficiarios_bpc_ativo', table_name='beneficiarios')
    op.drop_index('ix_beneficiarios_bf_ativo', table_name='beneficiarios')
    op.drop_index('ix_beneficiarios_ibge', table_name='beneficiarios')
    op.drop_index('ix_beneficiarios_nis', table_name='beneficiarios')
    op.drop_index('ix_beneficiarios_cpf_hash', table_name='beneficiarios')
    op.drop_table('beneficiarios')
