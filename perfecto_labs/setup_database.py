"""
Script de configuracion inicial de la base de datos.
Ejecutar una sola vez antes de usar la aplicacion.

Uso:
    python setup_database.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.seed import create_database, seed_data


def main():
    print("=" * 50)
    print("  Perfecto Labs - Configuracion de Base de Datos")
    print("=" * 50)
    print()
    print("Creando base de datos y tablas...")
    create_database()
    print()
    print("Insertando datos de ejemplo...")
    seed_data()
    print()
    print("=" * 50)
    print("  Configuracion completada exitosamente!")
    print("=" * 50)
    print()
    print("Ahora puede ejecutar la aplicacion con:")
    print("  python main.py")
    print()


if __name__ == "__main__":
    main()
