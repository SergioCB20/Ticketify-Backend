# -*- coding: utf-8 -*-
"""
Script para insertar usuarios asistentes de prueba
Útil para probar compras, tickets, etc.
"""

from app.core.database import SessionLocal
from app.models import User, Role
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_attendee_users():
    """Crear usuarios asistentes de prueba"""
    db = SessionLocal()
    
    try:
        # Verificar si ya existen asistentes
        existing_attendee = db.query(User).filter(User.email == "user1@test.com").first()
        if existing_attendee:
            print("⚠️  Los usuarios asistentes ya existen, saltando creación...")
            db.close()
            return
        
        # Obtener el rol de asistente
        attendee_role = db.query(Role).filter(Role.name == "Attendee").first()
        if not attendee_role:
            print("❌ Error: No existe el rol 'Attendee'. Ejecuta primero seed_initial_data.py")
            db.close()
            return
        
        attendees = [
            {
                "email": "user1@test.com",
                "password": get_password_hash("User123!"),
                "firstName": "Juan",
                "lastName": "Pérez",
                "phoneNumber": "+51912345001",
                "documentId": "70001234",
                "isActive": True
            },
            {
                "email": "user2@test.com",
                "password": get_password_hash("User123!"),
                "firstName": "María",
                "lastName": "García",
                "phoneNumber": "+51912345002",
                "documentId": "70001235",
                "isActive": True
            },
            {
                "email": "user3@test.com",
                "password": get_password_hash("User123!"),
                "firstName": "Pedro",
                "lastName": "López",
                "phoneNumber": "+51912345003",
                "documentId": "70001236",
                "isActive": True
            },
            {
                "email": "user4@test.com",
                "password": get_password_hash("User123!"),
                "firstName": "Ana",
                "lastName": "Martínez",
                "phoneNumber": "+51912345004",
                "documentId": "70001237",
                "isActive": True
            },
            {
                "email": "user5@test.com",
                "password": get_password_hash("User123!"),
                "firstName": "Luis",
                "lastName": "Sánchez",
                "phoneNumber": "+51912345005",
                "documentId": "70001238",
                "isActive": True
            },
            {
                "email": "user6@test.com",
                "password": get_password_hash("User123!"),
                "firstName": "Carmen",
                "lastName": "Rojas",
                "phoneNumber": "+51912345006",
                "documentId": "70001239",
                "isActive": True
            },
            {
                "email": "user7@test.com",
                "password": get_password_hash("User123!"),
                "firstName": "Roberto",
                "lastName": "Flores",
                "phoneNumber": "+51912345007",
                "documentId": "70001240",
                "isActive": True
            },
            {
                "email": "user8@test.com",
                "password": get_password_hash("User123!"),
                "firstName": "Laura",
                "lastName": "Torres",
                "phoneNumber": "+51912345008",
                "documentId": "70001241",
                "isActive": True
            },
            {
                "email": "user9@test.com",
                "password": get_password_hash("User123!"),
                "firstName": "Diego",
                "lastName": "Vargas",
                "phoneNumber": "+51912345009",
                "documentId": "70001242",
                "isActive": True
            },
            {
                "email": "user10@test.com",
                "password": get_password_hash("User123!"),
                "firstName": "Sofía",
                "lastName": "Castro",
                "phoneNumber": "+51912345010",
                "documentId": "70001243",
                "isActive": True
            }
        ]
        
        created_attendees = []
        for attendee_data in attendees:
            attendee = User(**attendee_data)
            attendee.roles.append(attendee_role)
            db.add(attendee)
            created_attendees.append(attendee)
        
        db.commit()
        
        print(f"✅ {len(created_attendees)} usuarios asistentes creados exitosamente\n")
        print("📋 LISTA DE USUARIOS:")
        for user in created_attendees:
            print(f"   • {user.email:<25} | {user.firstName} {user.lastName}")
        
        db.close()
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error al crear usuarios asistentes: {e}")
        db.close()


def main():
    """Ejecutar seeder de usuarios asistentes"""
    print("🌱 Creando usuarios asistentes de prueba...\n")
    print("=" * 70)
    
    create_attendee_users()
    
    print("\n" + "=" * 70)
    print("✅ Seeding completado!")
    print("\n📌 CREDENCIALES DE USUARIOS:")
    print("   Email: user1@test.com - user10@test.com")
    print("   Password: User123!")
    print("=" * 70)


if __name__ == "__main__":
    main()
