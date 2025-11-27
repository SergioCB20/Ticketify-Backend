"""
Script para crear índices optimizados en la base de datos
Mejora el performance de consultas de facturación
"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime


def upgrade():
    """
    Crear índices para optimización de facturación
    """
    
    # Índice compuesto para consultas de facturación
    # Usado en: get_event_purchases, calculate_event_revenue
    op.create_index(
        'idx_purchases_event_status',
        'purchases',
        ['event_id', 'status'],
        postgresql_using='btree'
    )
    
    # Índice para ordenamiento por fecha de pago
    # Usado en: cálculo de acreditaciones, reportes
    op.create_index(
        'idx_purchases_payment_date',
        'purchases',
        ['payment_date'],
        postgresql_using='btree',
        postgresql_where=sa.text("payment_date IS NOT NULL")
    )
    
    # Índice para búsquedas por fecha de creación (descendente)
    # Usado en: historial de transacciones
    op.create_index(
        'idx_purchases_created_at_desc',
        'purchases',
        [sa.text('created_at DESC')],
        postgresql_using='btree'
    )
    
    # Índice para consultas por usuario y evento
    # Usado en: historial de compras del usuario
    op.create_index(
        'idx_purchases_user_event',
        'purchases',
        ['user_id', 'event_id'],
        postgresql_using='btree'
    )
    
    # Índice para búsquedas por referencia de MercadoPago
    # Usado en: webhooks, sincronización
    op.create_index(
        'idx_purchases_payment_reference',
        'purchases',
        ['payment_reference'],
        postgresql_using='btree',
        postgresql_where=sa.text("payment_reference IS NOT NULL")
    )
    
    # Índice para consultas de eventos del organizador
    # Usado en: lista de eventos del organizador
    op.create_index(
        'idx_events_organizer',
        'events',
        ['organizer_id', 'status'],
        postgresql_using='btree'
    )
    
    # Índice para pagos por transacción
    # Usado en: consultas de pagos
    op.create_index(
        'idx_payments_transaction',
        'payments',
        ['transactionId'],
        postgresql_using='btree',
        postgresql_where=sa.text("\"transactionId\" IS NOT NULL")
    )
    
    print("✅ Índices creados exitosamente")


def downgrade():
    """
    Eliminar índices creados
    """
    op.drop_index('idx_purchases_event_status', table_name='purchases')
    op.drop_index('idx_purchases_payment_date', table_name='purchases')
    op.drop_index('idx_purchases_created_at_desc', table_name='purchases')
    op.drop_index('idx_purchases_user_event', table_name='purchases')
    op.drop_index('idx_purchases_payment_reference', table_name='purchases')
    op.drop_index('idx_events_organizer', table_name='events')
    op.drop_index('idx_payments_transaction', table_name='payments')
    
    print("✅ Índices eliminados exitosamente")


if __name__ == "__main__":
    """
    Script standalone para crear índices sin Alembic
    """
    from app.core.database import engine
    from sqlalchemy import text
    
    print("Creando índices de optimización...")
    
    with engine.connect() as conn:
        # Índices para purchases
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_purchases_event_status 
            ON purchases(event_id, status);
        """))
        
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_purchases_payment_date 
            ON purchases(payment_date) 
            WHERE payment_date IS NOT NULL;
        """))
        
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_purchases_created_at_desc 
            ON purchases(created_at DESC);
        """))
        
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_purchases_user_event 
            ON purchases(user_id, event_id);
        """))
        
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_purchases_payment_reference 
            ON purchases(payment_reference) 
            WHERE payment_reference IS NOT NULL;
        """))
        
        # Índices para events
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_events_organizer 
            ON events(organizer_id, status);
        """))
        
        # Índices para payments
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_payments_transaction 
            ON payments("transactionId") 
            WHERE "transactionId" IS NOT NULL;
        """))
        
        conn.commit()
        
        print("✅ Todos los índices creados exitosamente")
        print("\n📊 Índices creados:")
        print("   - idx_purchases_event_status")
        print("   - idx_purchases_payment_date")
        print("   - idx_purchases_created_at_desc")
        print("   - idx_purchases_user_event")
        print("   - idx_purchases_payment_reference")
        print("   - idx_events_organizer")
        print("   - idx_payments_transaction")
