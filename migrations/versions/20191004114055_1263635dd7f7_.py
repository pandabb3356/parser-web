"""add service table

Revision ID: 1263635dd7f7
Revises: b9bb012189ca
Create Date: 2019-10-04 11:40:55.738789

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '1263635dd7f7'
down_revision = 'b9bb012189ca'
branch_labels = None
depends_on = None


def upgrade():
    # add service table
    op.create_table('service',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('key', sa.Unicode(length=255), nullable=False),
                    sa.Column('name', sa.Unicode(length=255), nullable=False),
                    sa.Column('type', sa.SmallInteger, nullable=False),
                    sa.PrimaryKeyConstraint('id')
                    )


def downgrade():
    op.drop_table('service')
