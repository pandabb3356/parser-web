"""Create default user

Revision ID: 1b836149105b
Revises: ceffe233cfbf
Create Date: 2022-10-05 23:20:59.060905

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1b836149105b'
down_revision = 'ceffe233cfbf'
branch_labels = None
depends_on = None


def upgrade():
    user_no = "admin"
    user_name = "admin"
    # password: admin
    user_password = "$5$rounds=1000$G88P61gsVybVXP6t$63EWfI8gLn3kjXdR4djq96FilWtPQvJfRcVddzrnE69"
    user_email = "admin@test.test"

    op.execute(f"""
    INSERT INTO "public"."user" ("user_no", "password", "name", "active", "email") VALUES
    ('{user_no}', '{user_password}', '{user_name}', 'true', '{user_email}');
    """)


def downgrade():
    pass

