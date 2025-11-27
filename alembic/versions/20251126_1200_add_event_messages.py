"""add event_messages table

Revision ID: add_event_messages
Revises: 53533509121b
Create Date: 2025-11-26 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_event_messages'
down_revision = '53533509121b'
branch_labels = None
depends_on = None


def upgrade():
    # Crear enum para MessageType
    message_type_enum = postgresql.ENUM('INDIVIDUAL', 'BROADCAST', 'FILTERED', name='messagetype', create_type=True)
    message_type_enum.create(op.get_bind(), checkfirst=True)
    
    # Crear tabla event_messages
    op.create_table(
        'event_messages',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('subject', sa.String(length=200), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('message_type', message_type_enum, nullable=False),
        sa.Column('total_recipients', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('successful_sends', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('failed_sends', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('recipient_filters', sa.Text(), nullable=True),
        sa.Column('sent_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('event_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('organizer_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.ForeignKeyConstraint(['event_id'], ['events.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['organizer_id'], ['users.id']),
    )
    
    # Crear índices
    op.create_index('ix_event_messages_id', 'event_messages', ['id'])
    op.create_index('ix_event_messages_event_id', 'event_messages', ['event_id'])
    op.create_index('ix_event_messages_organizer_id', 'event_messages', ['organizer_id'])


def downgrade():
    # Eliminar índices
    op.drop_index('ix_event_messages_organizer_id', table_name='event_messages')
    op.drop_index('ix_event_messages_event_id', table_name='event_messages')
    op.drop_index('ix_event_messages_id', table_name='event_messages')
    
    # Eliminar tabla
    op.drop_table('event_messages')
    
    # Eliminar enum
    sa.Enum(name='messagetype').drop(op.get_bind(), checkfirst=True)
