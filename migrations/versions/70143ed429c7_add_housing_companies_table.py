"""Add housing_companies table

Revision ID: 70143ed429c7
Revises: 877ec1c85892
Create Date: 2025-01-14 11:26:38.794419

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '70143ed429c7'
down_revision = '877ec1c85892'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('housing_companies',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('address', sa.String(length=255), nullable=False),
    sa.Column('city', sa.String(length=100), nullable=False),
    sa.Column('postal_code', sa.String(length=20), nullable=False),
    sa.Column('manager_name', sa.String(length=100), nullable=True),
    sa.Column('manager_phone', sa.String(length=20), nullable=True),
    sa.Column('manager_email', sa.String(length=100), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('housing_companies')
    # ### end Alembic commands ###