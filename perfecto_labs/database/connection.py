"""
Modulo de conexion a MySQL para Perfecto Labs.
"""

import mysql.connector
from mysql.connector import Error

from config import DB_CONFIG


def get_connection():
    """Retorna una conexion activa a la base de datos."""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Error as e:
        print(f"Error al conectar a MySQL: {e}")
        return None


def execute_query(query, params=None, fetch=False, fetch_one=False):
    """Ejecuta una consulta SQL con manejo automatico de conexion."""
    conn = get_connection()
    if conn is None:
        return None
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query, params or ())
        if fetch_one:
            result = cursor.fetchone()
        elif fetch:
            result = cursor.fetchall()
        else:
            conn.commit()
            result = cursor.lastrowid
        return result
    except Error as e:
        print(f"Error en consulta: {e}")
        conn.rollback()
        return None
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()


def execute_many(query, data_list):
    """Ejecuta una consulta con multiples conjuntos de parametros."""
    conn = get_connection()
    if conn is None:
        return False
    try:
        cursor = conn.cursor()
        cursor.executemany(query, data_list)
        conn.commit()
        return True
    except Error as e:
        print(f"Error en consulta multiple: {e}")
        conn.rollback()
        return False
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()
