"""
Script para inicializar la base de datos y poblar datos de ejemplo.
"""

import os
import sys

import bcrypt
import mysql.connector
from mysql.connector import Error

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import DB_CONFIG


def create_database():
    """Crea la base de datos y ejecuta el esquema SQL."""
    schema_path = os.path.join(os.path.dirname(__file__), "schema.sql")
    try:
        conn = mysql.connector.connect(
            host=DB_CONFIG["host"],
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"],
        )
        cursor = conn.cursor()
        with open(schema_path, "r", encoding="utf-8") as f:
            sql_content = f.read()
        for statement in sql_content.split(";"):
            stmt = statement.strip()
            if stmt:
                cursor.execute(stmt)
        conn.commit()
        print("Base de datos y tablas creadas exitosamente.")
        cursor.close()
        conn.close()
    except Error as e:
        print(f"Error al crear la base de datos: {e}")
        sys.exit(1)


def seed_data():
    """Inserta datos de ejemplo en la base de datos."""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # --- Usuarios ---
        admin_pw = bcrypt.hashpw("admin123".encode(), bcrypt.gensalt()).decode()
        user_pw = bcrypt.hashpw("padre123".encode(), bcrypt.gensalt()).decode()

        usuarios = [
            ("admin", admin_pw, "Administrador General", "admin"),
            ("padre1", user_pw, "Juan Perez (Padre)", "user"),
            ("padre2", user_pw, "Maria Garcia (Madre)", "user"),
        ]
        cursor.executemany(
            "INSERT IGNORE INTO usuarios (username, password_hash, nombre_completo, rol) "
            "VALUES (%s, %s, %s, %s)",
            usuarios,
        )

        # --- Estudiantes ---
        estudiantes = [
            ("Carlos", "Martinez", 12, "Activo", "6to Primaria", "809-555-0101", "carlos.padre@email.com"),
            ("Ana", "Lopez", 10, "Activo", "4to Primaria", "809-555-0102", "ana.madre@email.com"),
            ("Luis", "Rodriguez", 14, "Intermedio", "2do Secundaria", "809-555-0103", "luis.padre@email.com"),
            ("Sofia", "Hernandez", 11, "Activo", "5to Primaria", "809-555-0104", "sofia.madre@email.com"),
            ("Miguel", "Perez", 13, "Bajo", "1ro Secundaria", "809-555-0105", "miguel.padre@email.com"),
            ("Valentina", "Diaz", 9, "Activo", "3ro Primaria", "809-555-0106", "val.madre@email.com"),
            ("Diego", "Sanchez", 15, "Intermedio", "3ro Secundaria", "809-555-0107", "diego.padre@email.com"),
            ("Isabella", "Ramirez", 8, "Activo", "2do Primaria", "809-555-0108", "isa.madre@email.com"),
            ("Andres", "Torres", 12, "Bajo", "6to Primaria", "809-555-0109", "andres.padre@email.com"),
            ("Camila", "Flores", 10, "Activo", "4to Primaria", "809-555-0110", "camila.madre@email.com"),
        ]
        cursor.executemany(
            "INSERT IGNORE INTO estudiantes (nombre, apellido, edad, rendimiento, grado, telefono_padre, email_padre) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s)",
            estudiantes,
        )

        # --- Inventario ---
        inventario = [
            ("Polo Shirt Blanco", "Polo shirt uniforme color blanco", "Uniformes", 450.00, 50, "polo_blanco.png"),
            ("Polo Shirt Azul", "Polo shirt uniforme color azul", "Uniformes", 450.00, 35, "polo_azul.png"),
            ("Pantalon Escolar", "Pantalon largo color khaki", "Uniformes", 600.00, 40, "pantalon.png"),
            ("Falda Escolar", "Falda plisada color khaki", "Uniformes", 550.00, 30, "falda.png"),
            ("Mochila Perfecto Labs", "Mochila escolar con logo", "Accesorios", 800.00, 20, "mochila.png"),
            ("Cuaderno 100 paginas", "Cuaderno rayado para notas", "Utiles", 75.00, 100, "cuaderno.png"),
            ("Lapicero Pack x3", "Pack de 3 lapiceros azul/negro/rojo", "Utiles", 50.00, 80, "lapiceros.png"),
            ("Gorra Perfecto Labs", "Gorra bordada con logo", "Accesorios", 350.00, 25, "gorra.png"),
            ("Termo Deportivo", "Termo de agua 500ml con logo", "Accesorios", 250.00, 40, "termo.png"),
            ("Kit de Arte", "Crayones, temperas, pinceles", "Utiles", 300.00, 15, "kit_arte.png"),
        ]
        cursor.executemany(
            "INSERT IGNORE INTO inventario (nombre, descripcion, categoria, precio, stock, imagen_path) "
            "VALUES (%s, %s, %s, %s, %s, %s)",
            inventario,
        )

        # --- Patrocinadores ---
        patrocinadores = [
            ("Pedro Almonte", "Almonte & Asociados", "809-555-0201", "pedro@almonte.com", 25000.00, "monetario"),
            ("Laura Mejia", "Supermercados La Fe", "809-555-0202", "laura@lafe.com", 15000.00, "especie"),
            ("Roberto Castillo", "Fundacion Educar", "809-555-0203", "roberto@educar.org", 50000.00, "monetario"),
            ("Carmen Nunez", "Farmacia Popular", "809-555-0204", "carmen@farmpop.com", 10000.00, "mixto"),
        ]
        cursor.executemany(
            "INSERT IGNORE INTO patrocinadores (nombre, empresa, telefono, email, monto_aporte, tipo_aporte) "
            "VALUES (%s, %s, %s, %s, %s, %s)",
            patrocinadores,
        )

        conn.commit()
        print("Datos de ejemplo insertados exitosamente.")
        print("\n--- Credenciales de acceso ---")
        print("Admin:   usuario='admin'   contrasena='admin123'")
        print("Padre:   usuario='padre1'  contrasena='padre123'")
        cursor.close()
        conn.close()

    except Error as e:
        print(f"Error al insertar datos: {e}")
        sys.exit(1)


if __name__ == "__main__":
    create_database()
    seed_data()
