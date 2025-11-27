-- Script SQL para poblar la base de datos con datos iniciales
-- Base de datos: nf1

USE nf1;

-- 1. Insertar localidades
INSERT INTO localidades (nombre, fecha_creacion, fecha_actualizacion) VALUES
('Arica', NOW(), NOW()),
('Iquique', NOW(), NOW()),
('Antofagasta', NOW(), NOW()),
('Copiapó', NOW(), NOW()),
('La Serena', NOW(), NOW()),
('Valparaíso', NOW(), NOW()),
('Santiago', NOW(), NOW()),
('Rancagua', NOW(), NOW()),
('Talca', NOW(), NOW()),
('Chillán', NOW(), NOW()),
('Concepción', NOW(), NOW()),
('Temuco', NOW(), NOW()),
('Valdivia', NOW(), NOW()),
('Puerto Montt', NOW(), NOW()),
('Coyhaique', NOW(), NOW()),
('Punta Arenas', NOW(), NOW()),
('Calama', NOW(), NOW()),
('Quillota', NOW(), NOW()),
('San Antonio', NOW(), NOW()),
('Melipilla', NOW(), NOW()),
('Curicó', NOW(), NOW()),
('Los Ángeles', NOW(), NOW()),
('Osorno', NOW(), NOW()),
('Puerto Varas', NOW(), NOW()),
('Castro', NOW(), NOW()),
('Ancud', NOW(), NOW()),
('Vallenar', NOW(), NOW()),
('Ovalle', NOW(), NOW()),
('San Fernando', NOW(), NOW()),
('Linares', NOW(), NOW()),
('Coronel', NOW(), NOW()),
('Talcahuano', NOW(), NOW()),
('Lota', NOW(), NOW()),
('Angol', NOW(), NOW()),
('Villarrica', NOW(), NOW()),
('Pucón', NOW(), NOW()),
('La Unión', NOW(), NOW()),
('Río Bueno', NOW(), NOW()),
('Quellón', NOW(), NOW()),
('Aysén', NOW(), NOW()),
('Porvenir', NOW(), NOW()),
('Natales', NOW(), NOW())
ON DUPLICATE KEY UPDATE nombre=VALUES(nombre);

-- 2. Insertar usuarios de ejemplo
-- Nota: Las contraseñas están hasheadas con Django, usa 'password123' para login
INSERT INTO usuarios (nombre, apellido, email, password, fecha_creacion, fecha_actualizacion, is_active, is_admin, puntos_friendly) VALUES
('Juan', 'Pérez', 'juan@example.com', 'pbkdf2_sha256$600000$OAiULfXGBN8kEqmLx8RkWP$Y9IjLFkJ3kCjA9+3xQn8QvK5vM7bN2cP0dR1eS2fT3g=', NOW(), NOW(), 1, 0, 0),
('María', 'González', 'maria@example.com', 'pbkdf2_sha256$600000$OAiULfXGBN8kEqmLx8RkWP$Y9IjLFkJ3kCjA9+3xQn8QvK5vM7bN2cP0dR1eS2fT3g=', NOW(), NOW(), 1, 0, 0),
('Carlos', 'Rodríguez', 'carlos@example.com', 'pbkdf2_sha256$600000$OAiULfXGBN8kEqmLx8RkWP$Y9IjLFkJ3kCjA9+3xQn8QvK5vM7bN2cP0dR1eS2fT3g=', NOW(), NOW(), 1, 0, 0),
('Ana', 'Martínez', 'ana@example.com', 'pbkdf2_sha256$600000$OAiULfXGBN8kEqmLx8RkWP$Y9IjLFkJ3kCjA9+3xQn8QvK5vM7bN2cP0dR1eS2fT3g=', NOW(), NOW(), 1, 0, 0),
('Luis', 'López', 'luis@example.com', 'pbkdf2_sha256$600000$OAiULfXGBN8kEqmLx8RkWP$Y9IjLFkJ3kCjA9+3xQn8QvK5vM7bN2cP0dR1eS2fT3g=', NOW(), NOW(), 1, 0, 0)
ON DUPLICATE KEY UPDATE nombre=VALUES(nombre);

-- 3. Insertar recintos de ejemplo
INSERT INTO recintos (nombre, direccion, id_localidad, fecha_creacion, fecha_actualizacion)
SELECT 'Estadio Nacional', 'Av. Grecia 2001, Santiago', id_localidad, NOW(), NOW()
FROM localidades WHERE nombre = 'Santiago'
ON DUPLICATE KEY UPDATE nombre=VALUES(nombre);

INSERT INTO recintos (nombre, direccion, id_localidad, fecha_creacion, fecha_actualizacion)
SELECT 'Complejo Deportivo Municipal', 'Av. Vicuña Mackenna 7500, Santiago', id_localidad, NOW(), NOW()
FROM localidades WHERE nombre = 'Santiago'
ON DUPLICATE KEY UPDATE nombre=VALUES(nombre);

INSERT INTO recintos (nombre, direccion, id_localidad, fecha_creacion, fecha_actualizacion)
SELECT 'Cancha El Sporting', 'Calle Los Carrera 123, Valparaíso', id_localidad, NOW(), NOW()
FROM localidades WHERE nombre = 'Valparaíso'
ON DUPLICATE KEY UPDATE nombre=VALUES(nombre);

INSERT INTO recintos (nombre, direccion, id_localidad, fecha_creacion, fecha_actualizacion)
SELECT 'Arena Deportiva', 'Av. Libertador 456, Concepción', id_localidad, NOW(), NOW()
FROM localidades WHERE nombre = 'Concepción'
ON DUPLICATE KEY UPDATE nombre=VALUES(nombre);

-- 4. Insertar canchas (3 canchas por cada recinto)
INSERT INTO canchas (nombre, tipo, id_recinto, fecha_creacion, fecha_actualizacion)
SELECT 'Cancha 1', 'Fútbol 11', id_recinto, NOW(), NOW()
FROM recintos WHERE nombre = 'Estadio Nacional'
ON DUPLICATE KEY UPDATE nombre=VALUES(nombre);

INSERT INTO canchas (nombre, tipo, id_recinto, fecha_creacion, fecha_actualizacion)
SELECT 'Cancha 2', 'Fútbol 7', id_recinto, NOW(), NOW()
FROM recintos WHERE nombre = 'Estadio Nacional'
ON DUPLICATE KEY UPDATE nombre=VALUES(nombre);

INSERT INTO canchas (nombre, tipo, id_recinto, fecha_creacion, fecha_actualizacion)
SELECT 'Cancha 3', 'Fútbol 11', id_recinto, NOW(), NOW()
FROM recintos WHERE nombre = 'Estadio Nacional'
ON DUPLICATE KEY UPDATE nombre=VALUES(nombre);

INSERT INTO canchas (nombre, tipo, id_recinto, fecha_creacion, fecha_actualizacion)
SELECT 'Cancha 1', 'Fútbol 11', id_recinto, NOW(), NOW()
FROM recintos WHERE nombre = 'Complejo Deportivo Municipal'
ON DUPLICATE KEY UPDATE nombre=VALUES(nombre);

INSERT INTO canchas (nombre, tipo, id_recinto, fecha_creacion, fecha_actualizacion)
SELECT 'Cancha 2', 'Fútbol 7', id_recinto, NOW(), NOW()
FROM recintos WHERE nombre = 'Complejo Deportivo Municipal'
ON DUPLICATE KEY UPDATE nombre=VALUES(nombre);

INSERT INTO canchas (nombre, tipo, id_recinto, fecha_creacion, fecha_actualizacion)
SELECT 'Cancha 3', 'Fútbol 11', id_recinto, NOW(), NOW()
FROM recintos WHERE nombre = 'Complejo Deportivo Municipal'
ON DUPLICATE KEY UPDATE nombre=VALUES(nombre);

INSERT INTO canchas (nombre, tipo, id_recinto, fecha_creacion, fecha_actualizacion)
SELECT 'Cancha 1', 'Fútbol 11', id_recinto, NOW(), NOW()
FROM recintos WHERE nombre = 'Cancha El Sporting'
ON DUPLICATE KEY UPDATE nombre=VALUES(nombre);

INSERT INTO canchas (nombre, tipo, id_recinto, fecha_creacion, fecha_actualizacion)
SELECT 'Cancha 2', 'Fútbol 7', id_recinto, NOW(), NOW()
FROM recintos WHERE nombre = 'Cancha El Sporting'
ON DUPLICATE KEY UPDATE nombre=VALUES(nombre);

INSERT INTO canchas (nombre, tipo, id_recinto, fecha_creacion, fecha_actualizacion)
SELECT 'Cancha 3', 'Fútbol 11', id_recinto, NOW(), NOW()
FROM recintos WHERE nombre = 'Cancha El Sporting'
ON DUPLICATE KEY UPDATE nombre=VALUES(nombre);

INSERT INTO canchas (nombre, tipo, id_recinto, fecha_creacion, fecha_actualizacion)
SELECT 'Cancha 1', 'Fútbol 11', id_recinto, NOW(), NOW()
FROM recintos WHERE nombre = 'Arena Deportiva'
ON DUPLICATE KEY UPDATE nombre=VALUES(nombre);

INSERT INTO canchas (nombre, tipo, id_recinto, fecha_creacion, fecha_actualizacion)
SELECT 'Cancha 2', 'Fútbol 7', id_recinto, NOW(), NOW()
FROM recintos WHERE nombre = 'Arena Deportiva'
ON DUPLICATE KEY UPDATE nombre=VALUES(nombre);

INSERT INTO canchas (nombre, tipo, id_recinto, fecha_creacion, fecha_actualizacion)
SELECT 'Cancha 3', 'Fútbol 11', id_recinto, NOW(), NOW()
FROM recintos WHERE nombre = 'Arena Deportiva'
ON DUPLICATE KEY UPDATE nombre=VALUES(nombre);

-- 5. Insertar partidos de ejemplo
INSERT INTO partidos (lugar, fecha_inicio, descripcion, max_jugadores, id_organizador, id_localidad, fecha_creacion, fecha_actualizacion)
SELECT 
    'Estadio Nacional - Santiago',
    DATE_ADD(NOW(), INTERVAL 2 DAY),
    'Partido amistoso de fútbol 7. Todos los niveles bienvenidos.',
    14,
    u.id_usuario,
    l.id_localidad,
    NOW(),
    NOW()
FROM usuarios u, localidades l
WHERE u.email = 'juan@example.com' AND l.nombre = 'Santiago'
LIMIT 1
ON DUPLICATE KEY UPDATE lugar=VALUES(lugar);

INSERT INTO partidos (lugar, fecha_inicio, descripcion, max_jugadores, id_organizador, id_localidad, fecha_creacion, fecha_actualizacion)
SELECT 
    'Complejo Municipal - Santiago',
    DATE_ADD(NOW(), INTERVAL 5 DAY),
    'Pichanga de fin de semana. Ven y juega!',
    10,
    u.id_usuario,
    l.id_localidad,
    NOW(),
    NOW()
FROM usuarios u, localidades l
WHERE u.email = 'maria@example.com' AND l.nombre = 'Santiago'
LIMIT 1
ON DUPLICATE KEY UPDATE lugar=VALUES(lugar);

INSERT INTO partidos (lugar, fecha_inicio, descripcion, max_jugadores, id_organizador, id_localidad, fecha_creacion, fecha_actualizacion)
SELECT 
    'Cancha El Sporting - Valparaíso',
    DATE_ADD(NOW(), INTERVAL 7 DAY),
    'Partido de fútbol 11. Buscamos jugadores para completar equipos.',
    22,
    u.id_usuario,
    l.id_localidad,
    NOW(),
    NOW()
FROM usuarios u, localidades l
WHERE u.email = 'carlos@example.com' AND l.nombre = 'Valparaíso'
LIMIT 1
ON DUPLICATE KEY UPDATE lugar=VALUES(lugar);

INSERT INTO partidos (lugar, fecha_inicio, descripcion, max_jugadores, id_organizador, id_localidad, fecha_creacion, fecha_actualizacion)
SELECT 
    'Arena Deportiva - Concepción',
    DATE_ADD(NOW(), INTERVAL 3 DAY),
    'Torneo relámpago. Inscripciones abiertas.',
    16,
    u.id_usuario,
    l.id_localidad,
    NOW(),
    NOW()
FROM usuarios u, localidades l
WHERE u.email = 'ana@example.com' AND l.nombre = 'Concepción'
LIMIT 1
ON DUPLICATE KEY UPDATE lugar=VALUES(lugar);

-- Verificar datos insertados
SELECT '=== RESUMEN DE DATOS ===' AS '';
SELECT CONCAT('Localidades: ', COUNT(*)) AS Total FROM localidades;
SELECT CONCAT('Usuarios: ', COUNT(*)) AS Total FROM usuarios;
SELECT CONCAT('Recintos: ', COUNT(*)) AS Total FROM recintos;
SELECT CONCAT('Canchas: ', COUNT(*)) AS Total FROM canchas;
SELECT CONCAT('Partidos: ', COUNT(*)) AS Total FROM partidos;

SELECT '¡Base de datos poblada exitosamente!' AS Resultado;
