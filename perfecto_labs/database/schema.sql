-- ============================================
-- Perfecto Labs - Database Schema
-- ============================================

CREATE DATABASE IF NOT EXISTS perfecto_labs
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE perfecto_labs;

-- -------------------------------------------
-- Tabla: usuarios (autenticacion y roles)
-- -------------------------------------------
CREATE TABLE IF NOT EXISTS usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    nombre_completo VARCHAR(100) NOT NULL,
    rol ENUM('admin', 'user') NOT NULL DEFAULT 'user',
    activo TINYINT(1) DEFAULT 1,
    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
    ultimo_acceso DATETIME NULL
) ENGINE=InnoDB;

-- -------------------------------------------
-- Tabla: estudiantes
-- -------------------------------------------
CREATE TABLE IF NOT EXISTS estudiantes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(60) NOT NULL,
    apellido VARCHAR(60) NOT NULL,
    edad INT NOT NULL,
    rendimiento ENUM('Activo', 'Intermedio', 'Bajo') NOT NULL DEFAULT 'Activo',
    grado VARCHAR(30) NULL,
    telefono_padre VARCHAR(20) NULL,
    email_padre VARCHAR(100) NULL,
    notas TEXT NULL,
    fecha_registro DATETIME DEFAULT CURRENT_TIMESTAMP,
    activo TINYINT(1) DEFAULT 1
) ENGINE=InnoDB;

-- -------------------------------------------
-- Tabla: inventario (articulos / productos)
-- -------------------------------------------
CREATE TABLE IF NOT EXISTS inventario (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT NULL,
    categoria VARCHAR(50) NULL,
    precio DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    stock INT NOT NULL DEFAULT 0,
    imagen_path VARCHAR(255) NULL,
    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
    activo TINYINT(1) DEFAULT 1
) ENGINE=InnoDB;

-- -------------------------------------------
-- Tabla: pedidos (ordenes de compra)
-- -------------------------------------------
CREATE TABLE IF NOT EXISTS pedidos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    numero_pedido VARCHAR(20) UNIQUE NOT NULL,
    cliente_nombre VARCHAR(100) NOT NULL,
    tipo ENUM('mensualidad', 'producto') NOT NULL,
    subtotal DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    impuesto DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    total DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    estado ENUM('pendiente', 'pagado', 'cancelado') DEFAULT 'pendiente',
    metodo_pago VARCHAR(30) NULL,
    usuario_id INT NULL,
    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE SET NULL
) ENGINE=InnoDB;

-- -------------------------------------------
-- Tabla: pedido_items (detalle de cada pedido)
-- -------------------------------------------
CREATE TABLE IF NOT EXISTS pedido_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    pedido_id INT NOT NULL,
    producto_id INT NULL,
    descripcion VARCHAR(200) NOT NULL,
    cantidad INT NOT NULL DEFAULT 1,
    precio_unitario DECIMAL(10, 2) NOT NULL,
    subtotal DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (pedido_id) REFERENCES pedidos(id) ON DELETE CASCADE,
    FOREIGN KEY (producto_id) REFERENCES inventario(id) ON DELETE SET NULL
) ENGINE=InnoDB;

-- -------------------------------------------
-- Tabla: patrocinadores
-- -------------------------------------------
CREATE TABLE IF NOT EXISTS patrocinadores (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    empresa VARCHAR(100) NULL,
    telefono VARCHAR(20) NULL,
    email VARCHAR(100) NULL,
    monto_aporte DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    tipo_aporte ENUM('monetario', 'especie', 'mixto') DEFAULT 'monetario',
    notas TEXT NULL,
    activo TINYINT(1) DEFAULT 1,
    fecha_registro DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- -------------------------------------------
-- Tabla: reportes_log (bitacora de movimientos)
-- -------------------------------------------
CREATE TABLE IF NOT EXISTS reportes_log (
    id INT AUTO_INCREMENT PRIMARY KEY,
    tipo ENUM('venta', 'pago_mensualidad', 'ingreso_inventario', 'patrocinio', 'otro') NOT NULL,
    descripcion TEXT NOT NULL,
    monto DECIMAL(10, 2) NULL,
    referencia_id INT NULL,
    usuario_id INT NULL,
    fecha DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE SET NULL
) ENGINE=InnoDB;
