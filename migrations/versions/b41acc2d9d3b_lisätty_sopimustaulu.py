"""Lisätty sopimustaulu

Revision ID: b41acc2d9d3b
Revises: a45997088485
Create Date: 2025-01-14 12:22:05.376584

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b41acc2d9d3b'
down_revision = 'a45997088485'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('contract',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('contract_type', sa.String(length=100), nullable=False),
    sa.Column('company_name', sa.String(length=255), nullable=False),
    sa.Column('housing_company_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['housing_company_id'], ['housing_companies.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('contract')
    # ### end Alembic commands ###
