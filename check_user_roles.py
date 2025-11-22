"""
Script para verificar los roles de un usuario específico
"""
import sys
import os

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.models.user import User
from app.models.role import Role

# Configurar la base de datos
engine = create_engine(str(settings.DATABASE_URL))
SessionLocal = sessionmaker(bind=engine)

def check_user_roles(email: str):
    """Verificar los roles de un usuario por email"""
    db = SessionLocal()
    try:
        # Buscar usuario
        user = db.query(User).filter(User.email == email).first()

        if not user:
            print(f"[ERROR] Usuario no encontrado: {email}")
            return

        print(f"[OK] Usuario encontrado:")
        print(f"   ID: {user.id}")
        print(f"   Email: {user.email}")
        print(f"   Nombre: {user.firstName} {user.lastName}")
        print(f"   Activo: {user.isActive}")
        print(f"\n[ROLES] Roles del usuario:")

        if not user.roles:
            print("   [WARN] NO TIENE ROLES ASIGNADOS")
        else:
            for role in user.roles:
                print(f"   - {role.name} (ID: {role.id})")

        # Verificar si es admin
        admin_roles = ['SUPER_ADMIN', 'SUPPORT_ADMIN', 'SECURITY_ADMIN', 'CONTENT_ADMIN']
        user_role_names = [role.name for role in user.roles] if user.roles else []
        is_admin = any(role in admin_roles for role in user_role_names)

        print(f"\n[ADMIN] Es administrador: {'SI' if is_admin else 'NO'}")

        # Mostrar todos los roles disponibles
        print(f"\n[SISTEMA] Roles disponibles en el sistema:")
        all_roles = db.query(Role).all()
        for role in all_roles:
            print(f"   - {role.name} (ID: {role.id})")

    finally:
        db.close()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        email = sys.argv[1]
    else:
        email = input("Ingresa el email del usuario: ")

    check_user_roles(email)
