# Perfecto Labs - Sistema de Gestion Profesional

Sistema completo de gestion educativa para **Perfecto Labs** con interfaz grafica moderna, base de datos MySQL y multiples modulos de administracion.

---

## Caracteristicas

- **Autenticacion con Roles**: Administrador (acceso total) y Usuario/Padre (acceso limitado)
- **Panel Principal**: Barra lateral vertical para navegacion entre modulos
- **Modulo Estudiantes**: Tabla con indicadores de rendimiento por colores (Verde=Activo, Amarillo=Intermedio, Rojo=Bajo)
- **Modulo Inventario**: Vista visual con tarjetas de productos, busqueda por nombre y agregar a pedido
- **Modulo Facturacion**: Pagos de mensualidad y productos, generacion automatica de PDF, soporte para impresora termica 80mm
- **Modulo Reportes**: Bitacora de ventas y movimientos semanales/mensuales
- **Modulo Patrocinadores**: Gestion completa de sponsors y aportes

---

## Requisitos Previos

- **Python** 3.10 o superior
- **MySQL Server** 8.0 o superior
- **Git** (opcional, para clonar el repositorio)

---

## Instalacion Paso a Paso

### 1. Instalar Python

#### Windows (PowerShell como Administrador)
```powershell
# Opcion A: Descargar desde https://www.python.org/downloads/
# Asegurate de marcar "Add Python to PATH" durante la instalacion

# Opcion B: Usando winget
winget install Python.Python.3.12

# Verificar instalacion
python --version
pip --version
```

#### macOS (Terminal)
```bash
# Usando Homebrew
brew install python

# Verificar
python3 --version
pip3 --version
```

#### Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install python3 python3-pip python3-tk -y

# Verificar
python3 --version
pip3 --version
```

---

### 2. Instalar MySQL Server

#### Windows (PowerShell como Administrador)
```powershell
# Opcion A: Descargar MySQL Installer desde https://dev.mysql.com/downloads/installer/
# Durante la instalacion, establecer la contrasena de root como: admin

# Opcion B: Usando winget
winget install Oracle.MySQL

# Opcion C: Usando Chocolatey
choco install mysql -y

# Iniciar el servicio MySQL
net start MySQL80
```

#### macOS (Terminal)
```bash
# Usando Homebrew
brew install mysql
brew services start mysql

# Establecer contrasena de root
mysql_secure_installation
# Cuando pregunte por nueva contrasena, escribir: admin
```

#### Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install mysql-server -y
sudo systemctl start mysql
sudo systemctl enable mysql

# Configurar contrasena de root
sudo mysql -e "ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'admin'; FLUSH PRIVILEGES;"
```

#### Verificar que MySQL funciona
```bash
mysql -u root -padmin -e "SELECT 'MySQL funcionando correctamente!' AS Estado;"
```

---

### 3. Clonar el Repositorio

```bash
git clone https://github.com/erielnicasio/ErielNicasio.git
cd ErielNicasio/perfecto_labs
```

---

### 4. Instalar Dependencias de Python

#### Windows (PowerShell / CMD)
```powershell
cd perfecto_labs
pip install -r requirements.txt
```

#### macOS / Linux
```bash
cd perfecto_labs
pip3 install -r requirements.txt
```

> **Nota**: Si tienes problemas con permisos, usa `pip install --user -r requirements.txt`

---

### 5. Configurar la Base de Datos

```bash
# Ejecutar el script de configuracion (crea la BD, tablas y datos de ejemplo)
python setup_database.py
```

Esto creara:
- La base de datos `perfecto_labs`
- Todas las tablas necesarias
- Usuarios de prueba
- Datos de ejemplo (estudiantes, inventario, patrocinadores)

---

### 6. Ejecutar la Aplicacion

```bash
python main.py
```

---

## Credenciales de Acceso

| Rol | Usuario | Contrasena |
|-----|---------|------------|
| Administrador | `admin` | `admin123` |
| Usuario/Padre | `padre1` | `padre123` |
| Usuario/Padre | `padre2` | `padre123` |

**Administrador**: Acceso completo a todos los modulos  
**Usuario/Padre**: Acceso a Estudiantes, Inventario y Facturacion (sin Reportes ni Patrocinadores)

---

## Configuracion de la Base de Datos

Si necesitas cambiar los datos de conexion a MySQL, edita el archivo `config.py`:

```python
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "admin",      # Cambia aqui tu contrasena
    "database": "perfecto_labs",
}
```

---

## Estructura del Proyecto

```
perfecto_labs/
├── main.py                    # Punto de entrada
├── config.py                  # Configuracion central
├── setup_database.py          # Script de configuracion de BD
├── requirements.txt           # Dependencias Python
├── README.md                  # Este archivo
├── database/
│   ├── __init__.py
│   ├── connection.py          # Conexion MySQL
│   ├── schema.sql             # Esquema de base de datos
│   └── seed.py                # Datos de ejemplo
├── auth/
│   ├── __init__.py
│   └── auth_manager.py        # Autenticacion y roles
├── gui/
│   ├── __init__.py
│   ├── login_window.py        # Ventana de login
│   ├── main_window.py         # Ventana principal + sidebar
│   ├── students.py            # Modulo Estudiantes
│   ├── inventory.py           # Modulo Inventario
│   ├── billing.py             # Modulo Facturacion
│   ├── reports.py             # Modulo Reportes
│   └── sponsors.py            # Modulo Patrocinadores
├── utils/
│   ├── __init__.py
│   ├── pdf_generator.py       # Generador de facturas PDF
│   └── printer.py             # Soporte impresora 80mm
└── assets/
    └── images/                # Imagenes de productos
```

---

## Modulos Detallados

### Estudiantes
- Tabla con nombre, apellido, edad, grado y rendimiento
- Indicador de rendimiento por colores: Verde (Activo), Amarillo (Intermedio), Rojo (Bajo)
- Busqueda en tiempo real por nombre/apellido
- Agregar, editar y eliminar estudiantes (solo Admin)

### Inventario
- Vista en tarjetas visuales con iconos por categoria
- Categorias: Uniformes, Accesorios, Utiles
- Busqueda por nombre con lupa
- Filtro por categoria
- Agregar productos al pedido con carrito de compras
- Gestion de stock

### Facturacion
- Crear facturas para productos o mensualidades
- Pago rapido de mensualidad por estudiante
- Generacion automatica de PDF (formato carta y 80mm)
- Enviar a impresora directamente
- Historial de facturas recientes
- Estadisticas de ventas del mes

### Reportes Generales
- Bitacora completa de ventas y movimientos
- Filtro por periodo: semanal, mensual o todo
- Filtro por tipo: ventas, mensualidades, patrocinios
- Resumen con tarjetas de totales
- Solo accesible para Administradores

### Patrocinadores
- Tabla de patrocinadores con datos de contacto
- Tipos de aporte: monetario, en especie, mixto
- Resumen de aportes totales
- Busqueda por nombre/empresa
- Solo accesible para Administradores

---

## Impresora Termica 80mm

El sistema soporta impresion directa a impresoras termicas de 80mm:

### Windows
1. Instalar los drivers de la impresora termica
2. Configurarla como impresora predeterminada
3. Al presionar el boton de imprimir, el PDF se enviara automaticamente

### Linux
```bash
# Verificar que la impresora esta detectada
lpstat -p

# Si usa USB, puede necesitar permisos
sudo usermod -a -G lpadmin $USER
```

---

## Solucion de Problemas

### Error de conexion a MySQL
```bash
# Verificar que MySQL esta corriendo
# Windows:
net start MySQL80

# Linux:
sudo systemctl status mysql
sudo systemctl start mysql

# macOS:
brew services start mysql
```

### Error "Access denied for user 'root'"
```bash
# Restablecer la contrasena de root
sudo mysql
ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'admin';
FLUSH PRIVILEGES;
EXIT;
```

### Error con tkinter
```bash
# Linux - instalar tkinter
sudo apt install python3-tk -y

# macOS con Homebrew
brew install python-tk
```

### Error con dependencias de Python
```bash
# Actualizar pip primero
pip install --upgrade pip

# Reinstalar dependencias
pip install -r requirements.txt --force-reinstall
```

---

## Tecnologias Utilizadas

| Tecnologia | Uso |
|-----------|-----|
| Python 3 | Lenguaje principal |
| CustomTkinter | Interfaz grafica moderna |
| MySQL 8 | Base de datos relacional |
| fpdf2 | Generacion de facturas PDF |
| bcrypt | Encriptacion de contrasenas |
| Pillow | Manejo de imagenes |
| python-escpos | Soporte impresora termica |

---

## Licencia

Desarrollado para **Perfecto Labs** - Todos los derechos reservados 2026.
