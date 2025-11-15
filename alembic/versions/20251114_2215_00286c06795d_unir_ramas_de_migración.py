"""Unir ramas de migración

Revision ID: 00286c06795d
Revises: 2e35c595fa24, a41d8524fd5e
Create Date: 2025-11-14 22:15:51.907979

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '00286c06795d'
down_revision = ('2e35c595fa24', 'a41d8524fd5e')
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
