"""add pedidos table

Revision ID: 002
Revises: 001
Create Date: 2024-12-25

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'pedidos',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('numero', sa.String(10), nullable=True),
        sa.Column('cpf_cidadao', sa.String(11), nullable=False),
        sa.Column('nome_cidadao', sa.String(200), nullable=True),
        sa.Column('telefone_cidadao', sa.String(15), nullable=True),
        sa.Column('farmacia_id', sa.String(50), nullable=False),
        sa.Column('farmacia_nome', sa.String(200), nullable=True),
        sa.Column('farmacia_whatsapp', sa.String(15), nullable=True),
        sa.Column('medicamentos', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('receita_url', sa.Text(), nullable=True),
        sa.Column('status', sa.String(20), nullable=True),
        sa.Column('criado_em', sa.DateTime(), nullable=True),
        sa.Column('atualizado_em', sa.DateTime(), nullable=True),
        sa.Column('confirmado_em', sa.DateTime(), nullable=True),
        sa.Column('pronto_em', sa.DateTime(), nullable=True),
        sa.Column('retirado_em', sa.DateTime(), nullable=True),
        sa.Column('twilio_sid_farmacia', sa.String(50), nullable=True),
        sa.Column('twilio_sid_cidadao', sa.String(50), nullable=True),
        sa.Column('observacoes', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_pedidos_cpf_cidadao', 'pedidos', ['cpf_cidadao'], unique=False)
    op.create_index('ix_pedidos_numero', 'pedidos', ['numero'], unique=True)
    op.create_index('ix_pedidos_status', 'pedidos', ['status'], unique=False)


def downgrade() -> None:
    op.drop_index('ix_pedidos_status', table_name='pedidos')
    op.drop_index('ix_pedidos_numero', table_name='pedidos')
    op.drop_index('ix_pedidos_cpf_cidadao', table_name='pedidos')
    op.drop_table('pedidos')
