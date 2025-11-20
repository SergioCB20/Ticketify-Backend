"""change qrCode to binary

Revision ID: a9ac77d5c307
Revises: ffb7293ddaf3
Create Date: 2025-11-19 23:48:57.536649

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a9ac77d5c307'
down_revision = 'ffb7293ddaf3'
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
