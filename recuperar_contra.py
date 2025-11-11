from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

# Genera el hash para la nueva contraseña que elijas:
new_password = "Password123#"   # cámbialo por la que quieras
print(get_password_hash(new_password))
