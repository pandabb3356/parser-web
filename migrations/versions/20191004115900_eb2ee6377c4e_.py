"""add org_id field to record_data

Revision ID: eb2ee6377c4e
Revises: 1263635dd7f7
Create Date: 2019-10-04 11:59:00.520254

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'eb2ee6377c4e'
down_revision = '1263635dd7f7'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('record_data', sa.Column('org_id', sa.Integer(), nullable=True))


def downgrade():
    op.drop_column('record_data', 'org_id')
