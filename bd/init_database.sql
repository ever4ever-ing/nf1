-- ============================================
-- NF1 - SCRIPT DE INICIALIZACIÓN COMPLETO
-- ============================================
-- Este script crea toda la base de datos y estructura de tablas
-- Incluye: Base de datos, usuarios, localidades, canchas, partidos,
--          mensajes, notificaciones, equipos y estadísticas
-- ============================================

-- Crear base de datos
CREATE DATABASE IF NOT EXISTS nf1;
USE nf1;

-- ============================================
-- TABLAS PRINCIPALES
-- ============================================

-- Tabla de usuarios
CREATE TABLE IF NOT EXISTS usuarios (
    id_usuario INT PRIMARY KEY AUTO_INCREMENT,
    nombre VARCHAR(100) NOT NULL,
    apellido VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    is_active TINYINT(1) NOT NULL DEFAULT 1,
    is_admin TINYINT(1) NOT NULL DEFAULT 0,
    foto_perfil VARCHAR(100) DEFAULT NULL,
    fecha_nacimiento DATE DEFAULT NULL,
    hobbies TEXT DEFAULT NULL,
    biografia TEXT DEFAULT NULL,
    puntos_friendly INT NOT NULL DEFAULT 0,
    last_login DATETIME(6) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tabla de localidades
CREATE TABLE IF NOT EXISTS localidades (
    id_localidad BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
    nombre VARCHAR(100) NOT NULL,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Insertar localidades de Chile
INSERT INTO localidades (nombre) VALUES 
('Arica'), ('Iquique'), ('Antofagasta'), ('Copiapó'), ('La Serena'),
('Valparaíso'), ('Santiago'), ('Rancagua'), ('Talca'), ('Chillán'),
('Concepción'), ('Temuco'), ('Valdivia'), ('Puerto Montt'), ('Coyhaique'),
('Punta Arenas'), ('Calama'), ('Quillota'), ('San Antonio'), ('Melipilla'),
('Curicó'), ('Los Ángeles'), ('Osorno'), ('Puerto Varas'), ('Castro'),
('Ancud'), ('Vallenar'), ('Ovalle'), ('San Fernando'), ('Linares'),
('Coronel'), ('Talcahuano'), ('Lota'), ('Angol'), ('Villarrica'),
('Pucón'), ('La Unión'), ('Río Bueno'), ('Quellón'), ('Aysén'),
('Porvenir'), ('Natales')
ON DUPLICATE KEY UPDATE nombre = VALUES(nombre);

-- ============================================
-- TABLAS DE INFRAESTRUCTURA
-- ============================================

-- Tabla de recintos
CREATE TABLE IF NOT EXISTS recintos (
    id_recinto BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
    nombre VARCHAR(100) NOT NULL,
    direccion TEXT NOT NULL,
    id_localidad BIGINT UNSIGNED NOT NULL,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_localidad) REFERENCES localidades(id_localidad)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tabla de canchas
CREATE TABLE IF NOT EXISTS canchas (
    id_cancha BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
    nombre VARCHAR(100) NOT NULL,
    id_recinto BIGINT UNSIGNED NOT NULL,
    tipo VARCHAR(50),
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_recinto) REFERENCES recintos(id_recinto)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tabla de reservas
CREATE TABLE IF NOT EXISTS reservas (
    id_reserva BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
    id_cancha BIGINT UNSIGNED NOT NULL,
    id_recinto BIGINT UNSIGNED NOT NULL,
    id_usuario INT NOT NULL,
    fecha_reserva TIMESTAMP NOT NULL,
    hora_inicio TIME NOT NULL,
    hora_fin TIME NOT NULL,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_cancha) REFERENCES canchas(id_cancha),
    FOREIGN KEY (id_recinto) REFERENCES recintos(id_recinto),
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- TABLAS DE PARTIDOS FRIENDLY
-- ============================================

-- Tabla de partidos
CREATE TABLE IF NOT EXISTS partidos (
    id_partido INT PRIMARY KEY AUTO_INCREMENT,
    lugar VARCHAR(100) NOT NULL,
    fecha_inicio DATETIME NULL DEFAULT NULL,
    descripcion TEXT,
    max_jugadores INT DEFAULT 10,
    id_organizador INT NOT NULL,
    id_localidad BIGINT UNSIGNED NOT NULL,
    id_reserva BIGINT UNSIGNED NULL DEFAULT NULL,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (id_organizador) REFERENCES usuarios(id_usuario),
    FOREIGN KEY (id_localidad) REFERENCES localidades(id_localidad),
    FOREIGN KEY (id_reserva) REFERENCES reservas(id_reserva)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tabla de participantes en partidos
CREATE TABLE IF NOT EXISTS participantes_partido (
    id_participante INT PRIMARY KEY AUTO_INCREMENT,
    id_partido INT NOT NULL,
    id_usuario INT NOT NULL,
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_partido) REFERENCES partidos(id_partido),
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tabla de mensajes de partido
CREATE TABLE IF NOT EXISTS eventos_mensajepartido (
    id_mensaje INT PRIMARY KEY AUTO_INCREMENT,
    id_partido_id INT NOT NULL,
    id_usuario_id INT NOT NULL,
    mensaje TEXT NOT NULL,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_partido_id) REFERENCES partidos(id_partido) ON DELETE CASCADE,
    FOREIGN KEY (id_usuario_id) REFERENCES usuarios(id_usuario) ON DELETE CASCADE,
    INDEX idx_partido (id_partido_id),
    INDEX idx_fecha (fecha_creacion)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tabla de notificaciones
CREATE TABLE IF NOT EXISTS notificaciones (
    id_notificacion INT NOT NULL AUTO_INCREMENT,
    id_usuario_id INT NOT NULL,
    id_partido_id INT NOT NULL,
    tipo VARCHAR(50) NOT NULL,
    mensaje TEXT NOT NULL,
    leida TINYINT(1) NOT NULL DEFAULT 0,
    fecha_creacion DATETIME(6) NOT NULL,
    id_usuario_relacionado_id INT DEFAULT NULL,
    id_mensaje_id INT DEFAULT NULL,
    PRIMARY KEY (id_notificacion),
    KEY notificaciones_id_usuario_id (id_usuario_id),
    KEY notificaciones_id_partido_id (id_partido_id),
    KEY notificaciones_id_usuario_relacionado_id (id_usuario_relacionado_id),
    KEY notificaciones_id_mensaje_id (id_mensaje_id),
    KEY notificaciones_fecha_creacion (fecha_creacion),
    CONSTRAINT notificaciones_id_usuario_fk FOREIGN KEY (id_usuario_id) REFERENCES usuarios (id_usuario) ON DELETE CASCADE,
    CONSTRAINT notificaciones_id_partido_fk FOREIGN KEY (id_partido_id) REFERENCES partidos (id_partido) ON DELETE CASCADE,
    CONSTRAINT notificaciones_id_usuario_relacionado_fk FOREIGN KEY (id_usuario_relacionado_id) REFERENCES usuarios (id_usuario) ON DELETE CASCADE,
    CONSTRAINT notificaciones_id_mensaje_fk FOREIGN KEY (id_mensaje_id) REFERENCES eventos_mensajepartido (id_mensaje) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- ============================================
-- TABLAS DE MODO COMPETITIVO
-- ============================================

-- Tabla de equipos
CREATE TABLE IF NOT EXISTS equipos (
    id_equipo INT NOT NULL AUTO_INCREMENT,
    nombre VARCHAR(100) NOT NULL,
    logo VARCHAR(100) DEFAULT NULL,
    descripcion TEXT,
    id_anfitrion_id INT NOT NULL,
    fecha_creacion DATETIME(6) NOT NULL,
    activo TINYINT(1) NOT NULL DEFAULT 1,
    color_primario VARCHAR(7) NOT NULL DEFAULT '#007bff',
    color_secundario VARCHAR(7) NOT NULL DEFAULT '#ffffff',
    PRIMARY KEY (id_equipo),
    KEY equipos_id_anfitrion_id (id_anfitrion_id),
    CONSTRAINT equipos_id_anfitrion_fk FOREIGN KEY (id_anfitrion_id) REFERENCES usuarios (id_usuario) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Tabla de miembros de equipo
CREATE TABLE IF NOT EXISTS miembros_equipo (
    id_miembro INT NOT NULL AUTO_INCREMENT,
    id_equipo_id INT NOT NULL,
    id_usuario_id INT NOT NULL,
    rol VARCHAR(20) NOT NULL DEFAULT 'jugador',
    numero_camiseta INT DEFAULT NULL,
    fecha_union DATETIME(6) NOT NULL,
    activo TINYINT(1) NOT NULL DEFAULT 1,
    PRIMARY KEY (id_miembro),
    UNIQUE KEY miembros_equipo_id_equipo_id_usuario (id_equipo_id, id_usuario_id),
    KEY miembros_equipo_id_equipo_id (id_equipo_id),
    KEY miembros_equipo_id_usuario_id (id_usuario_id),
    CONSTRAINT miembros_equipo_id_equipo_fk FOREIGN KEY (id_equipo_id) REFERENCES equipos (id_equipo) ON DELETE CASCADE,
    CONSTRAINT miembros_equipo_id_usuario_fk FOREIGN KEY (id_usuario_id) REFERENCES usuarios (id_usuario) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Tabla de partidos competitivos
CREATE TABLE IF NOT EXISTS partidos_competitivos (
    id_partido INT NOT NULL AUTO_INCREMENT,
    nombre VARCHAR(200) NOT NULL,
    descripcion TEXT,
    id_equipo_local_id INT NOT NULL,
    id_equipo_visitante_id INT NOT NULL,
    id_cancha_id BIGINT UNSIGNED DEFAULT NULL,
    id_localidad_id BIGINT UNSIGNED DEFAULT NULL,
    lugar VARCHAR(200) NOT NULL,
    fecha_hora DATETIME(6) NOT NULL,
    goles_local INT NOT NULL DEFAULT 0,
    goles_visitante INT NOT NULL DEFAULT 0,
    estado VARCHAR(20) NOT NULL DEFAULT 'programado',
    id_creador_id INT NOT NULL,
    fecha_creacion DATETIME(6) NOT NULL,
    fecha_actualizacion DATETIME(6) NOT NULL,
    PRIMARY KEY (id_partido),
    KEY partidos_competitivos_id_equipo_local_id (id_equipo_local_id),
    KEY partidos_competitivos_id_equipo_visitante_id (id_equipo_visitante_id),
    KEY partidos_competitivos_id_cancha_id (id_cancha_id),
    KEY partidos_competitivos_id_localidad_id (id_localidad_id),
    KEY partidos_competitivos_id_creador_id (id_creador_id),
    CONSTRAINT partidos_competitivos_id_equipo_local_fk FOREIGN KEY (id_equipo_local_id) REFERENCES equipos (id_equipo) ON DELETE CASCADE,
    CONSTRAINT partidos_competitivos_id_equipo_visitante_fk FOREIGN KEY (id_equipo_visitante_id) REFERENCES equipos (id_equipo) ON DELETE CASCADE,
    CONSTRAINT partidos_competitivos_id_cancha_fk FOREIGN KEY (id_cancha_id) REFERENCES canchas (id_cancha) ON DELETE SET NULL,
    CONSTRAINT partidos_competitivos_id_localidad_fk FOREIGN KEY (id_localidad_id) REFERENCES localidades (id_localidad) ON DELETE SET NULL,
    CONSTRAINT partidos_competitivos_id_creador_fk FOREIGN KEY (id_creador_id) REFERENCES usuarios (id_usuario) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Tabla de invitaciones a equipos
CREATE TABLE IF NOT EXISTS invitaciones_equipo (
    id_invitacion INT NOT NULL AUTO_INCREMENT,
    id_equipo_id INT NOT NULL,
    id_usuario_id INT NOT NULL,
    id_invitador_id INT NOT NULL,
    mensaje TEXT,
    estado VARCHAR(20) NOT NULL DEFAULT 'pendiente',
    fecha_invitacion DATETIME(6) NOT NULL,
    fecha_respuesta DATETIME(6) DEFAULT NULL,
    PRIMARY KEY (id_invitacion),
    UNIQUE KEY invitaciones_equipo_id_equipo_id_usuario (id_equipo_id, id_usuario_id),
    KEY invitaciones_equipo_id_equipo_id (id_equipo_id),
    KEY invitaciones_equipo_id_usuario_id (id_usuario_id),
    KEY invitaciones_equipo_id_invitador_id (id_invitador_id),
    CONSTRAINT invitaciones_equipo_id_equipo_fk FOREIGN KEY (id_equipo_id) REFERENCES equipos (id_equipo) ON DELETE CASCADE,
    CONSTRAINT invitaciones_equipo_id_usuario_fk FOREIGN KEY (id_usuario_id) REFERENCES usuarios (id_usuario) ON DELETE CASCADE,
    CONSTRAINT invitaciones_equipo_id_invitador_fk FOREIGN KEY (id_invitador_id) REFERENCES usuarios (id_usuario) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Tabla de estadísticas de jugadores
CREATE TABLE IF NOT EXISTS estadisticas_jugador (
    id_estadistica INT NOT NULL AUTO_INCREMENT,
    id_partido_id INT NOT NULL,
    id_usuario_id INT NOT NULL,
    id_equipo_id INT NOT NULL,
    goles INT NOT NULL DEFAULT 0,
    asistencias INT NOT NULL DEFAULT 0,
    tarjetas_amarillas INT NOT NULL DEFAULT 0,
    tarjetas_rojas INT NOT NULL DEFAULT 0,
    PRIMARY KEY (id_estadistica),
    UNIQUE KEY estadisticas_jugador_id_partido_id_usuario (id_partido_id, id_usuario_id),
    KEY estadisticas_jugador_id_partido_id (id_partido_id),
    KEY estadisticas_jugador_id_usuario_id (id_usuario_id),
    KEY estadisticas_jugador_id_equipo_id (id_equipo_id),
    CONSTRAINT estadisticas_jugador_id_partido_fk FOREIGN KEY (id_partido_id) REFERENCES partidos_competitivos (id_partido) ON DELETE CASCADE,
    CONSTRAINT estadisticas_jugador_id_usuario_fk FOREIGN KEY (id_usuario_id) REFERENCES usuarios (id_usuario) ON DELETE CASCADE,
    CONSTRAINT estadisticas_jugador_id_equipo_fk FOREIGN KEY (id_equipo_id) REFERENCES equipos (id_equipo) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- ============================================
-- FIN DEL SCRIPT
-- ============================================

