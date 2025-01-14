"""Add phone and apartment to User table

Revision ID: 877ec1c85892
Revises: a8c3f26f008f
Create Date: 2025-01-14 10:57:26.360891

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '877ec1c85892'
down_revision = 'a8c3f26f008f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('phone', sa.String(length=15), nullable=True))
        batch_op.add_column(sa.Column('apartment', sa.String(length=5), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_column('apartment')
        batch_op.drop_column('phone')

    # ### end Alembic commands ###