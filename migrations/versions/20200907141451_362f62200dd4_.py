"""add tc_default_org_id to org table

Revision ID: 362f62200dd4
Revises: 935fcdc19394
Create Date: 2020-09-07 14:14:51.486550

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '362f62200dd4'
down_revision = '935fcdc19394'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('org', sa.Column('tc_default_org_id', sa.Integer(), nullable=False, server_default="1", default="1"))


def downgrade():
    op.drop_column('org', 'tc_default_org_id')
