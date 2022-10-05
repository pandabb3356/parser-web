"""add org and record table

Revision ID: ab13049a779c
Revises: 
Create Date: 2019-10-03 14:02:56.228671

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'ab13049a779c'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # add org table
    op.create_table('org',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('name', sa.Unicode(length=255), nullable=False),
                    sa.Column('protocol', sa.Unicode(length=10), nullable=False),
                    sa.Column('domain', sa.Unicode(length=255), nullable=False),
                    sa.Column('code', sa.Unicode(length=100), nullable=False),
                    sa.Column('public_cloud', sa.Boolean(), nullable=True),
                    sa.Column('deleted', sa.Boolean(), nullable=True),
                    sa.PrimaryKeyConstraint('id')
                    )

    # add record table
    op.create_table('record',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('type', sa.SmallInteger(), nullable=True),
                    sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=True),
                    sa.PrimaryKeyConstraint('id')
                    )


def downgrade():
    op.drop_table('record')
    op.drop_table('org')
