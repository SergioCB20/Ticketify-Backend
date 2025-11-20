"""change qrCode to binary

Revision ID: 410f7dcd7e08
Revises: a9ac77d5c307
Create Date: 2025-11-19 23:51:27.583609

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '410f7dcd7e08'
down_revision = 'a9ac77d5c307'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
        ALTER TABLE tickets
        ALTER COLUMN "qrCode" TYPE bytea
        USING NULL
    """)   


def downgrade() -> None:
    op.execute("""
        ALTER TABLE tickets
        ALTER COLUMN "qrCode" TYPE varchar
        USING encode("qrCode", 'base64')
    """)
