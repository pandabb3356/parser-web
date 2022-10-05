"""add record_data and add completeness and status fields to record

Revision ID: b9bb012189ca
Revises: ab13049a779c
Create Date: 2019-10-04 10:47:37.078902

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'b9bb012189ca'
down_revision = 'ab13049a779c'
branch_labels = None
depends_on = None


def upgrade():
    # add record_data table
    op.create_table('record_data',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('record_id', sa.Integer(), nullable=False),
                    sa.Column('data', sa.TEXT, nullable=True),
                    sa.PrimaryKeyConstraint('id')
                    )

    # add record fields
    op.add_column('record',
                  sa.Column('completeness', sa.DECIMAL(precision=5, scale=2), nullable=True, server_default='0')
                  )
    op.add_column('record', sa.Column('status', sa.SmallInteger, nullable=False, server_default='1'))


def downgrade():
    op.drop_column('record', 'status')
    op.drop_column('record', 'completeness')

    op.drop_table('record_data')
