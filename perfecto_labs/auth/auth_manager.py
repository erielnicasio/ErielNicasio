"""
Modulo de autenticacion y gestion de roles.
"""

import bcrypt

from database.connection import execute_query


def authenticate(username, password):
    """Autentica un usuario y retorna sus datos si es valido."""
    user = execute_query(
        "SELECT id, username, password_hash, nombre_completo, rol, activo "
        "FROM usuarios WHERE username = %s",
        (username,),
        fetch_one=True,
    )
    if user is None:
        return None, "Usuario no encontrado."
    if not user["activo"]:
        return None, "Cuenta desactivada. Contacte al administrador."
    if not bcrypt.checkpw(password.encode(), user["password_hash"].encode()):
        return None, "Contrasena incorrecta."

    execute_query(
        "UPDATE usuarios SET ultimo_acceso = NOW() WHERE id = %s",
        (user["id"],),
    )
    return user, "Acceso exitoso."


def create_user(username, password, nombre_completo, rol="user"):
    """Crea un nuevo usuario en el sistema."""
    password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    result = execute_query(
        "INSERT INTO usuarios (username, password_hash, nombre_completo, rol) "
        "VALUES (%s, %s, %s, %s)",
        (username, password_hash, nombre_completo, rol),
    )
    return result is not None


def get_all_users():
    """Retorna todos los usuarios del sistema."""
    return execute_query(
        "SELECT id, username, nombre_completo, rol, activo, fecha_creacion, ultimo_acceso "
        "FROM usuarios ORDER BY id",
        fetch=True,
    ) or []


def toggle_user_status(user_id):
    """Activa/desactiva un usuario."""
    execute_query(
        "UPDATE usuarios SET activo = NOT activo WHERE id = %s",
        (user_id,),
    )
