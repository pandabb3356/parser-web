"""add user table

Revision ID: ceffe233cfbf
Revises: 362f62200dd4
Create Date: 2021-04-06 16:17:29.890619

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "ceffe233cfbf"
down_revision = "362f62200dd4"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "user",
        sa.Column("id", sa.Integer(), nullable=False, primary_key=True, autoincrement=True),
        sa.Column("user_no", sa.Unicode(length=255), nullable=False),
        sa.Column("password", sa.Unicode(length=255), nullable=True),
        sa.Column("name", sa.Unicode(length=255), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=True, default='0'),
        sa.Column("email", sa.Unicode(length=255), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade():
    op.drop_table("user")
