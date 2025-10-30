"""Renombrar hashed_password a password en users

Revision ID: 0f8c51d82a8d
Revises: 
Create Date: 2025-10-26 09:02:27.605204

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '0f8c51d82a8d'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # --- VERIFICATIONS (MODIFICADO) ---
    op.drop_index('ix_verifications_id', table_name='verifications')
    op.drop_index('ix_verifications_token', table_name='verifications')
    # op.drop_table('verifications') # <-- Esto fallaría
    op.execute('DROP TABLE verifications CASCADE') # <-- Arreglado

    # --- PURCHASES (MODIFICADO) ---
    op.drop_index('ix_purchases_id', table_name='purchases')
    op.execute('DROP TABLE purchases CASCADE') # <-- Arreglado

    # --- PROMOTIONS (MODIFICADO) ---
    op.drop_index('ix_promotions_code', table_name='promotions')
    op.drop_index('ix_promotions_id', table_name='promotions')
    # op.drop_table('promotions') # <-- Esto fallaría
    op.execute('DROP TABLE promotions CASCADE') # <-- Arreglado

    # --- EVENTS (Sin cambios) ---
    op.add_column('events', sa.Column('startDate', sa.DateTime(timezone=True), nullable=False))
    op.add_column('events', sa.Column('endDate', sa.DateTime(timezone=True), nullable=False))
    op.add_column('events', sa.Column('venue', sa.String(length=200), nullable=False))
    op.add_column('events', sa.Column('totalCapacity', sa.Integer(), nullable=False))
    op.add_column('events', sa.Column('multimedia', sa.ARRAY(sa.String()), nullable=True))
    op.add_column('events', sa.Column('createdAt', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False))
    op.add_column('events', sa.Column('updatedAt', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False))
    op.drop_index('ix_events_slug', table_name='events')
    op.drop_column('events', 'location')
    op.drop_column('events', 'slug')
    op.drop_column('events', 'is_featured')
    op.drop_column('events', 'short_description')
    op.drop_column('events', 'tags')
    op.drop_column('events', 'is_active')
    op.drop_column('events', 'base_price')
    op.drop_column('events', 'banner_url')
    op.drop_column('events', 'updated_at')
    op.drop_column('events', 'date')
    op.drop_column('events', 'address')
    op.drop_column('events', 'image_url')
    op.drop_column('events', 'created_at')
    op.drop_column('events', 'capacity')
    op.drop_column('events', 'city')
    op.drop_column('events', 'country')
    op.drop_column('events', 'published_at')

    # --- NOTIFICATIONS (Sin cambios) ---
    op.add_column('notifications', sa.Column('metaData', sa.Text(), nullable=True))
    op.drop_column('notifications', 'meta_data')

    # --- TICKETS (Sin cambios) ---
    op.add_column('tickets', sa.Column('price', sa.Numeric(precision=10, scale=2), nullable=False))
    op.add_column('tickets', sa.Column('qrCode', sa.String(), nullable=True))
    op.add_column('tickets', sa.Column('purchaseDate', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False))
    op.add_column('tickets', sa.Column('isValid', sa.Boolean(), nullable=False))
    op.add_column('tickets', sa.Column('createdAt', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False))
    op.add_column('tickets', sa.Column('updatedAt', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False))
    op.add_column('tickets', sa.Column('payment_id', sa.UUID(), nullable=False))
    op.drop_index('ix_tickets_ticket_number', table_name='tickets')
    op.drop_constraint('tickets_original_owner_id_fkey', 'tickets', type_='foreignkey')
    # op.drop_constraint('tickets_purchase_id_fkey', 'tickets', type_='foreignkey') # <-- Correctamente comentado
    op.create_foreign_key(None, 'tickets', 'payments', ['payment_id'], ['id'])
    op.drop_column('tickets', 'used_at')
    op.drop_column('tickets', 'seat_number')
    op.drop_column('tickets', 'ticket_number')
    op.drop_column('tickets', 'expires_at')
    op.drop_column('tickets', 'row_number')
    op.drop_column('tickets', 'purchase_id')
    op.drop_column('tickets', 'transferred_at')
    op.drop_column('tickets', 'is_transferable')
    op.drop_column('tickets', 'section')
    op.drop_column('tickets', 'created_at')
    op.drop_column('tickets', 'barcode')
    op.drop_column('tickets', 'entry_gate')
    op.drop_column('tickets', 'transfer_reason')
    op.drop_column('tickets', 'original_owner_id')
    op.drop_column('tickets', 'validated_by')
    op.drop_column('tickets', 'notes')
    op.drop_column('tickets', 'qr_code')
    op.drop_column('tickets', 'is_refundable')
    op.drop_column('tickets', 'special_requirements')
    op.drop_column('tickets', 'updated_at')

    # --- USERS (MODIFICADO) ---
    # op.add_column('users', sa.Column('password', sa.String(length=255), nullable=False)) # <-- Eliminado
    op.add_column('users', sa.Column('firstName', sa.String(length=100), nullable=False))
    op.add_column('users', sa.Column('lastName', sa.String(length=100), nullable=False))
    op.add_column('users', sa.Column('phoneNumber', sa.String(length=20), nullable=True))
    op.add_column('users', sa.Column('documentId', sa.String(length=50), nullable=True))
    op.add_column('users', sa.Column('profilePhoto', sa.String(length=500), nullable=True))
    op.add_column('users', sa.Column('isActive', sa.Boolean(), nullable=False))
    op.add_column('users', sa.Column('createdAt', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False))
    op.add_column('users', sa.Column('lastLogin', sa.DateTime(timezone=True), nullable=True))
    op.drop_column('users', 'role')
    op.drop_column('users', 'verification_token')
    op.drop_column('users', 'is_active')
    op.drop_column('users', 'last_login')
    op.drop_column('users', 'avatar')
    op.drop_column('users', 'reset_token')
    op.drop_column('users', 'last_name')
    op.drop_column('users', 'first_name')
    
    # op.drop_column('users', 'hashed_password') # <-- Reemplazado por alter_column
    
    # --- ARREGLO PARA RENOMBRAR PASSWORD (MODIFICADO) ---
    op.alter_column(
        'users',
        'hashed_password',
        new_column_name='password',
        existing_type=sa.String(length=255),
        nullable=False
    )
    # --- FIN ARREGLO ---
    
    op.drop_column('users', 'reset_token_expires')
    op.drop_column('users', 'updated_at')
    op.drop_column('users', 'login_count')
    op.drop_column('users', 'verification_token_expires')
    op.drop_column('users', 'is_verified')
    op.drop_column('users', 'created_at')
    # ### end Alembic commands ###
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), autoincrement=False, nullable=False))
    op.add_column('users', sa.Column('is_verified', sa.BOOLEAN(), autoincrement=False, nullable=False))
    op.add_column('users', sa.Column('verification_token_expires', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=True))
    op.add_column('users', sa.Column('login_count', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.add_column('users', sa.Column('updated_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), autoincrement=False, nullable=False))
    op.add_column('users', sa.Column('reset_token_expires', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=True))
    op.add_column('users', sa.Column('hashed_password', sa.VARCHAR(length=255), autoincrement=False, nullable=False))
    op.add_column('users', sa.Column('first_name', sa.VARCHAR(length=50), autoincrement=False, nullable=False))
    op.add_column('users', sa.Column('last_name', sa.VARCHAR(length=50), autoincrement=False, nullable=False))
    op.add_column('users', sa.Column('reset_token', sa.VARCHAR(length=255), autoincrement=False, nullable=True))
    op.add_column('users', sa.Column('avatar', sa.VARCHAR(length=255), autoincrement=False, nullable=True))
    op.add_column('users', sa.Column('last_login', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=True))
    op.add_column('users', sa.Column('is_active', sa.BOOLEAN(), autoincrement=False, nullable=False))
    op.add_column('users', sa.Column('verification_token', sa.VARCHAR(length=255), autoincrement=False, nullable=True))
    op.add_column('users', sa.Column('role', postgresql.ENUM('ADMIN', 'ORGANIZER', 'CUSTOMER', name='userrole'), autoincrement=False, nullable=False))
    op.drop_column('users', 'lastLogin')
    op.drop_column('users', 'createdAt')
    op.drop_column('users', 'isActive')
    op.drop_column('users', 'profilePhoto')
    op.drop_column('users', 'documentId')
    op.drop_column('users', 'phoneNumber')
    op.drop_column('users', 'lastName')
    op.drop_column('users', 'firstName')
    op.drop_column('users', 'password')
    op.add_column('tickets', sa.Column('updated_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), autoincrement=False, nullable=False))
    op.add_column('tickets', sa.Column('special_requirements', sa.TEXT(), autoincrement=False, nullable=True))
    op.add_column('tickets', sa.Column('is_refundable', sa.BOOLEAN(), autoincrement=False, nullable=False))
    op.add_column('tickets', sa.Column('qr_code', sa.TEXT(), autoincrement=False, nullable=True))
    op.add_column('tickets', sa.Column('notes', sa.TEXT(), autoincrement=False, nullable=True))
    op.add_column('tickets', sa.Column('validated_by', sa.VARCHAR(length=255), autoincrement=False, nullable=True))
    op.add_column('tickets', sa.Column('original_owner_id', sa.UUID(), autoincrement=False, nullable=True))
    op.add_column('tickets', sa.Column('transfer_reason', sa.TEXT(), autoincrement=False, nullable=True))
    op.add_column('tickets', sa.Column('entry_gate', sa.VARCHAR(length=50), autoincrement=False, nullable=True))
    op.add_column('tickets', sa.Column('barcode', sa.VARCHAR(length=100), autoincrement=False, nullable=True))
    op.add_column('tickets', sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), autoincrement=False, nullable=False))
    op.add_column('tickets', sa.Column('section', sa.VARCHAR(length=50), autoincrement=False, nullable=True))
    op.add_column('tickets', sa.Column('is_transferable', sa.BOOLEAN(), autoincrement=False, nullable=False))
    op.add_column('tickets', sa.Column('transferred_at', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=True))
    op.add_column('tickets', sa.Column('purchase_id', sa.UUID(), autoincrement=False, nullable=False))
    op.add_column('tickets', sa.Column('row_number', sa.VARCHAR(length=10), autoincrement=False, nullable=True))
    op.add_column('tickets', sa.Column('expires_at', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=True))
    op.add_column('tickets', sa.Column('ticket_number', sa.VARCHAR(length=50), autoincrement=False, nullable=False))
    op.add_column('tickets', sa.Column('seat_number', sa.VARCHAR(length=20), autoincrement=False, nullable=True))
    op.add_column('tickets', sa.Column('used_at', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=True))
    op.drop_constraint(None, 'tickets', type_='foreignkey')
    op.create_foreign_key('tickets_purchase_id_fkey', 'tickets', 'purchases', ['purchase_id'], ['id'])
    op.create_foreign_key('tickets_original_owner_id_fkey', 'tickets', 'users', ['original_owner_id'], ['id'])
    op.create_index('ix_tickets_ticket_number', 'tickets', ['ticket_number'], unique=False)
    op.drop_column('tickets', 'payment_id')
    op.drop_column('tickets', 'updatedAt')
    op.drop_column('tickets', 'createdAt')
    op.drop_column('tickets', 'isValid')
    op.drop_column('tickets', 'purchaseDate')
    op.drop_column('tickets', 'qrCode')
    op.drop_column('tickets', 'price')
    op.add_column('notifications', sa.Column('meta_data', sa.TEXT(), autoincrement=False, nullable=True))
    op.drop_column('notifications', 'metaData')
    op.add_column('events', sa.Column('published_at', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=True))
    op.add_column('events', sa.Column('country', sa.VARCHAR(length=100), autoincrement=False, nullable=False))
    op.add_column('events', sa.Column('city', sa.VARCHAR(length=100), autoincrement=False, nullable=False))
    op.add_column('events', sa.Column('capacity', sa.INTEGER(), autoincrement=False, nullable=False))
    op.add_column('events', sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), autoincrement=False, nullable=False))
    op.add_column('events', sa.Column('image_url', sa.VARCHAR(length=500), autoincrement=False, nullable=True))
    op.add_column('events', sa.Column('address', sa.TEXT(), autoincrement=False, nullable=True))
    op.add_column('events', sa.Column('date', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=False))
    op.add_column('events', sa.Column('updated_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), autoincrement=False, nullable=False))
    op.add_column('events', sa.Column('banner_url', sa.VARCHAR(length=500), autoincrement=False, nullable=True))
    op.add_column('events', sa.Column('base_price', sa.NUMERIC(precision=10, scale=2), autoincrement=False, nullable=False))
    op.add_column('events', sa.Column('is_active', sa.BOOLEAN(), autoincrement=False, nullable=False))
    op.add_column('events', sa.Column('tags', sa.VARCHAR(length=500), autoincrement=False, nullable=True))
    op.add_column('events', sa.Column('short_description', sa.VARCHAR(length=500), autoincrement=False, nullable=True))
    op.add_column('events', sa.Column('is_featured', sa.BOOLEAN(), autoincrement=False, nullable=False))
    op.add_column('events', sa.Column('slug', sa.VARCHAR(length=255), autoincrement=False, nullable=True))
    op.add_column('events', sa.Column('location', sa.VARCHAR(length=200), autoincrement=False, nullable=False))
    op.create_index('ix_events_slug', 'events', ['slug'], unique=False)
    op.drop_column('events', 'updatedAt')
    op.drop_column('events', 'createdAt')
    op.drop_column('events', 'multimedia')
    op.drop_column('events', 'totalCapacity')
    op.drop_column('events', 'venue')
    op.drop_column('events', 'endDate')
    op.drop_column('events', 'startDate')
    op.create_table('promotions',
    sa.Column('id', sa.UUID(), autoincrement=False, nullable=False),
    sa.Column('name', sa.VARCHAR(length=200), autoincrement=False, nullable=False),
    sa.Column('description', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('code', sa.VARCHAR(length=50), autoincrement=False, nullable=False),
    sa.Column('promotion_type', postgresql.ENUM('PERCENTAGE', 'FIXED_AMOUNT', 'BUY_ONE_GET_ONE', 'EARLY_BIRD', name='promotiontype'), autoincrement=False, nullable=False),
    sa.Column('discount_value', sa.NUMERIC(precision=10, scale=2), autoincrement=False, nullable=False),
    sa.Column('max_discount_amount', sa.NUMERIC(precision=10, scale=2), autoincrement=False, nullable=True),
    sa.Column('min_purchase_amount', sa.NUMERIC(precision=10, scale=2), autoincrement=False, nullable=True),
    sa.Column('max_uses', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('max_uses_per_user', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('current_uses', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('start_date', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=False),
    sa.Column('end_date', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=False),
    sa.Column('applies_to_all_events', sa.BOOLEAN(), autoincrement=False, nullable=False),
    sa.Column('applies_to_new_users_only', sa.BOOLEAN(), autoincrement=False, nullable=False),
    sa.Column('status', postgresql.ENUM('ACTIVE', 'INACTIVE', 'EXPIRED', 'USED_UP', name='promotionstatus'), autoincrement=False, nullable=False),
    sa.Column('is_public', sa.BOOLEAN(), autoincrement=False, nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), autoincrement=False, nullable=False),
    sa.Column('updated_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), autoincrement=False, nullable=False),
    sa.Column('created_by_id', sa.UUID(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['created_by_id'], ['users.id'], name='promotions_created_by_id_fkey'),
    sa.PrimaryKeyConstraint('id', name='promotions_pkey'),
    postgresql_ignore_search_path=False
    )
    op.create_index('ix_promotions_id', 'promotions', ['id'], unique=False)
    op.create_index('ix_promotions_code', 'promotions', ['code'], unique=False)
    op.create_table('purchases',
    sa.Column('id', sa.UUID(), autoincrement=False, nullable=False),
    sa.Column('total_amount', sa.NUMERIC(precision=10, scale=2), autoincrement=False, nullable=False),
    sa.Column('subtotal', sa.NUMERIC(precision=10, scale=2), autoincrement=False, nullable=False),
    sa.Column('tax_amount', sa.NUMERIC(precision=10, scale=2), autoincrement=False, nullable=False),
    sa.Column('service_fee', sa.NUMERIC(precision=10, scale=2), autoincrement=False, nullable=False),
    sa.Column('discount_amount', sa.NUMERIC(precision=10, scale=2), autoincrement=False, nullable=False),
    sa.Column('quantity', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('unit_price', sa.NUMERIC(precision=10, scale=2), autoincrement=False, nullable=False),
    sa.Column('status', postgresql.ENUM('PENDING', 'PROCESSING', 'COMPLETED', 'FAILED', 'CANCELLED', 'REFUNDED', name='purchasestatus'), autoincrement=False, nullable=False),
    sa.Column('payment_method', postgresql.ENUM('CREDIT_CARD', 'DEBIT_CARD', 'MERCADOPAGO', 'PAYPAL', 'BANK_TRANSFER', name='paymentmethod'), autoincrement=False, nullable=True),
    sa.Column('payment_reference', sa.VARCHAR(length=255), autoincrement=False, nullable=True),
    sa.Column('buyer_email', sa.VARCHAR(length=255), autoincrement=False, nullable=False),
    sa.Column('buyer_phone', sa.VARCHAR(length=20), autoincrement=False, nullable=True),
    sa.Column('buyer_document', sa.VARCHAR(length=20), autoincrement=False, nullable=True),
    sa.Column('billing_name', sa.VARCHAR(length=200), autoincrement=False, nullable=True),
    sa.Column('billing_address', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('billing_city', sa.VARCHAR(length=100), autoincrement=False, nullable=True),
    sa.Column('billing_country', sa.VARCHAR(length=100), autoincrement=False, nullable=True),
    sa.Column('purchase_date', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), autoincrement=False, nullable=False),
    sa.Column('payment_date', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=True),
    sa.Column('confirmation_date', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=True),
    sa.Column('notes', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('refund_reason', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), autoincrement=False, nullable=False),
    sa.Column('updated_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), autoincrement=False, nullable=False),
    sa.Column('user_id', sa.UUID(), autoincrement=False, nullable=False),
    sa.Column('event_id', sa.UUID(), autoincrement=False, nullable=False),
    sa.Column('ticket_type_id', sa.UUID(), autoincrement=False, nullable=False),
    sa.Column('promotion_id', sa.UUID(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['event_id'], ['events.id'], name='purchases_event_id_fkey'),
    sa.ForeignKeyConstraint(['promotion_id'], ['promotions.id'], name='purchases_promotion_id_fkey'),
    sa.ForeignKeyConstraint(['ticket_type_id'], ['ticket_types.id'], name='purchases_ticket_type_id_fkey'),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], name='purchases_user_id_fkey'),
    sa.PrimaryKeyConstraint('id', name='purchases_pkey')
    )
    op.create_index('ix_purchases_id', 'purchases', ['id'], unique=False)
    op.create_table('verifications',
    sa.Column('id', sa.UUID(), autoincrement=False, nullable=False),
    sa.Column('verification_type', postgresql.ENUM('EMAIL_VERIFICATION', 'PASSWORD_RESET', 'PHONE_VERIFICATION', 'TWO_FACTOR_AUTH', 'ACCOUNT_RECOVERY', name='verificationtype'), autoincrement=False, nullable=False),
    sa.Column('token', sa.VARCHAR(length=255), autoincrement=False, nullable=False),
    sa.Column('code', sa.VARCHAR(length=10), autoincrement=False, nullable=True),
    sa.Column('email', sa.VARCHAR(length=255), autoincrement=False, nullable=True),
    sa.Column('phone', sa.VARCHAR(length=20), autoincrement=False, nullable=True),
    sa.Column('status', postgresql.ENUM('PENDING', 'VERIFIED', 'EXPIRED', 'FAILED', name='verificationstatus'), autoincrement=False, nullable=False),
    sa.Column('attempts', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('max_attempts', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), autoincrement=False, nullable=False),
    sa.Column('updated_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), autoincrement=False, nullable=False),
    sa.Column('expires_at', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=False),
    sa.Column('verified_at', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=True),
    sa.Column('meta_data', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('ip_address', sa.VARCHAR(length=45), autoincrement=False, nullable=True),
    sa.Column('user_agent', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('user_id', sa.UUID(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], name='verifications_user_id_fkey'),
    sa.PrimaryKeyConstraint('id', name='verifications_pkey')
    )
    op.create_index('ix_verifications_token', 'verifications', ['token'], unique=False)
    op.create_index('ix_verifications_id', 'verifications', ['id'], unique=False)
    # ### end Alembic commands ###
