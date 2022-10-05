"""add tronclass_toggle table

Revision ID: 935fcdc19394
Revises: eb2ee6377c4e
Create Date: 2019-10-07 20:41:08.892602

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '935fcdc19394'
down_revision = 'eb2ee6377c4e'
branch_labels = None
depends_on = None


def upgrade():
    # add tronclass_toggle table
    op.create_table('tronclass_toggle',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('feature_toggle_name', sa.Unicode(length=255), nullable=False),
                    sa.Column('description', sa.Unicode(length=200), nullable=True),
                    sa.Column('default_value', sa.Boolean(), nullable=True, default='0'),
                    sa.PrimaryKeyConstraint('id'),
                    sa.UniqueConstraint('feature_toggle_name')
                    )


def downgrade():
    op.drop_table('tronclass_toggle')
