"""
Script para generar una clave Fernet para encriptación
Ejecutar: python generate_fernet_key.py
"""

from cryptography.fernet import Fernet

# Generar una nueva clave
key = Fernet.generate_key()

print("=" * 60)
print("🔑 FERNET KEY GENERADA")
print("=" * 60)
print("\nCopia esta clave y agrégala a tu archivo .env:")
print(f"\nFERNET_KEY={key.decode()}")
print("\n" + "=" * 60)
