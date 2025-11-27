CREATE DATABASE IF NOT EXISTS nf1;
USE nf1;

-- Tabla de usuarios
CREATE TABLE usuarios (
    id_usuario INT PRIMARY KEY AUTO_INCREMENT,
    nombre VARCHAR(100) NOT NULL,
    apellido VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE localidades (
    id_localidad SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP NOT NULL
);

-- Insertar todas las localidades de Chile
INSERT INTO localidades (nombre) VALUES 
('Arica'),
('Iquique'),
('Antofagasta'),
('Copiapó'),
('La Serena'),
('Valparaíso'),
('Santiago'),
('Rancagua'),
('Talca'),
('Chillán'),
('Concepción'),
('Temuco'),
('Valdivia'),
('Puerto Montt'),
('Coyhaique'),
('Punta Arenas'),
('Calama'),
('Quillota'),
('San Antonio'),
('Melipilla'),
('Curicó'),
('Los Ángeles'),
('Osorno'),
('Puerto Varas'),
('Castro'),
('Ancud'),
('Vallenar'),
('Ovalle'),
('San Fernando'),
('Linares'),
('Coronel'),
('Talcahuano'),
('Lota'),
('Angol'),
('Villarrica'),
('Pucón'),
('La Unión'),
('Río Bueno'),
('Quellón'),
('Aysén'),
('Porvenir'),
('Natales');


CREATE TABLE recintos (
    id_recinto SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    direccion TEXT NOT NULL,
    id_localidad BIGINT UNSIGNED NOT NULL, -- Cambiado a BIGINT UNSIGNED
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP NOT NULL,
    FOREIGN KEY (id_localidad) REFERENCES localidades(id_localidad)
);

CREATE TABLE canchas (
    id_cancha SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    id_recinto BIGINT UNSIGNED NOT NULL,
    tipo VARCHAR(50),
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP NOT NULL,
    FOREIGN KEY (id_recinto) REFERENCES recintos(id_recinto)
);

CREATE TABLE reservas (
    id_reserva SERIAL PRIMARY KEY,
    id_cancha BIGINT UNSIGNED NOT NULL,
    id_recinto BIGINT UNSIGNED NOT NULL,
    id_usuario INT NOT NULL, -- Cambiado a INT para ser compatible con la tabla usuarios
    fecha_reserva TIMESTAMP NOT NULL,
    hora_inicio TIME NOT NULL, -- Nueva columna para la hora de inicio
    hora_fin TIME NOT NULL, -- Nueva columna para la hora de fin
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP NOT NULL,
    FOREIGN KEY (id_cancha) REFERENCES canchas(id_cancha),
    FOREIGN KEY (id_recinto) REFERENCES recintos(id_recinto),
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario)
);


CREATE TABLE partidos (
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
);

-- Tabla de participantes
CREATE TABLE participantes_partido (
    id_participante INT PRIMARY KEY AUTO_INCREMENT,
    id_partido INT NOT NULL,
    id_usuario INT NOT NULL,
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_partido) REFERENCES partidos(id_partido),
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario)
);
