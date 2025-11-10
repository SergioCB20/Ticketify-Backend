from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from app.models.role import Role
from app.models.permission import Permission
from app.models.user import AdminRole # Para el enum AdminRole

class RoleRepository:
    """
    Repositorio para todas las operaciones de base de datos
    relacionadas con los Roles.
    """
    
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, role_id: UUID) -> Optional[Role]:
        """Obtiene un rol por su ID."""
        return self.db.query(Role).filter(Role.id == role_id).first()

    def get_by_name(self, role_name: str | AdminRole) -> Optional[Role]:
        """
        Obtiene un rol por su nombre.
        Acepta un string o un enum AdminRole.
        """
        name = role_name.value if isinstance(role_name, AdminRole) else role_name
        return self.db.query(Role).filter(Role.name == name).first()

    def get_all(self, skip: int = 0, limit: int = 100) -> List[Role]:
        """Obtiene una lista de todos los roles."""
        return self.db.query(Role).order_by(Role.name).offset(skip).limit(limit).all()

    def create_role(self, name: str, description: Optional[str] = None) -> Role:
        """
        Crea un nuevo rol en la base de datos.
        Sigue el patrón del repo de User y hace commit.
        """
        new_role = Role(name=name, description=description)
        self.db.add(new_role)
        self.db.commit()
        self.db.refresh(new_role)
        return new_role

    def update_role(self, role: Role, description: str) -> Role:
        """Actualiza la descripción de un rol."""
        role.description = description
        self.db.commit()
        self.db.refresh(role)
        return role

    def delete_role(self, role_id: UUID) -> bool:
        """Elimina un rol por su ID."""
        role = self.get_by_id(role_id)
        if not role:
            return False
        
        # Opcional: Verificar si el rol está en uso antes de borrar
        if role.users:
            raise ValueError(f"No se puede eliminar el rol '{role.name}' porque está asignado a usuarios.")
            
        self.db.delete(role)
        self.db.commit()
        return True

    def assign_permission_to_role(self, role: Role, permission: Permission) -> Role:
        """Asigna un permiso a un rol."""
        if permission not in role.permissions:
            role.permissions.append(permission)
            self.db.commit()
            self.db.refresh(role)
        return role

    def revoke_permission_from_role(self, role: Role, permission: Permission) -> Role:
        """Revoca un permiso de un rol."""
        if permission in role.permissions:
            role.permissions.remove(permission)
            self.db.commit()
            self.db.refresh(role)
        return role