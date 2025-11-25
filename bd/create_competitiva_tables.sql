-- Crear tablas para la app competitiva

-- Tabla de equipos
CREATE TABLE IF NOT EXISTS `equipos` (
  `id_equipo` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) NOT NULL,
  `logo` varchar(100) DEFAULT NULL,
  `descripcion` text,
  `id_anfitrion_id` int NOT NULL,
  `fecha_creacion` datetime(6) NOT NULL,
  `activo` tinyint(1) NOT NULL DEFAULT 1,
  `color_primario` varchar(7) NOT NULL DEFAULT '#007bff',
  `color_secundario` varchar(7) NOT NULL DEFAULT '#ffffff',
  PRIMARY KEY (`id_equipo`),
  KEY `equipos_id_anfitrion_id` (`id_anfitrion_id`),
  CONSTRAINT `equipos_id_anfitrion_fk` FOREIGN KEY (`id_anfitrion_id`) REFERENCES `usuarios` (`id_usuario`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Tabla de miembros de equipo
CREATE TABLE IF NOT EXISTS `miembros_equipo` (
  `id_miembro` int NOT NULL AUTO_INCREMENT,
  `id_equipo_id` int NOT NULL,
  `id_usuario_id` int NOT NULL,
  `rol` varchar(20) NOT NULL DEFAULT 'jugador',
  `numero_camiseta` int DEFAULT NULL,
  `fecha_union` datetime(6) NOT NULL,
  `activo` tinyint(1) NOT NULL DEFAULT 1,
  PRIMARY KEY (`id_miembro`),
  UNIQUE KEY `miembros_equipo_id_equipo_id_usuario` (`id_equipo_id`, `id_usuario_id`),
  KEY `miembros_equipo_id_equipo_id` (`id_equipo_id`),
  KEY `miembros_equipo_id_usuario_id` (`id_usuario_id`),
  CONSTRAINT `miembros_equipo_id_equipo_fk` FOREIGN KEY (`id_equipo_id`) REFERENCES `equipos` (`id_equipo`) ON DELETE CASCADE,
  CONSTRAINT `miembros_equipo_id_usuario_fk` FOREIGN KEY (`id_usuario_id`) REFERENCES `usuarios` (`id_usuario`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Tabla de partidos competitivos
CREATE TABLE IF NOT EXISTS `partidos_competitivos` (
  `id_partido` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(200) NOT NULL,
  `descripcion` text,
  `id_equipo_local_id` int NOT NULL,
  `id_equipo_visitante_id` int NOT NULL,
  `id_cancha_id` bigint DEFAULT NULL,
  `id_localidad_id` bigint DEFAULT NULL,
  `lugar` varchar(200) NOT NULL,
  `fecha_hora` datetime(6) NOT NULL,
  `goles_local` int NOT NULL DEFAULT 0,
  `goles_visitante` int NOT NULL DEFAULT 0,
  `estado` varchar(20) NOT NULL DEFAULT 'programado',
  `id_creador_id` int NOT NULL,
  `fecha_creacion` datetime(6) NOT NULL,
  `fecha_actualizacion` datetime(6) NOT NULL,
  PRIMARY KEY (`id_partido`),
  KEY `partidos_competitivos_id_equipo_local_id` (`id_equipo_local_id`),
  KEY `partidos_competitivos_id_equipo_visitante_id` (`id_equipo_visitante_id`),
  KEY `partidos_competitivos_id_cancha_id` (`id_cancha_id`),
  KEY `partidos_competitivos_id_localidad_id` (`id_localidad_id`),
  KEY `partidos_competitivos_id_creador_id` (`id_creador_id`),
  CONSTRAINT `partidos_competitivos_id_equipo_local_fk` FOREIGN KEY (`id_equipo_local_id`) REFERENCES `equipos` (`id_equipo`) ON DELETE CASCADE,
  CONSTRAINT `partidos_competitivos_id_equipo_visitante_fk` FOREIGN KEY (`id_equipo_visitante_id`) REFERENCES `equipos` (`id_equipo`) ON DELETE CASCADE,
  CONSTRAINT `partidos_competitivos_id_cancha_fk` FOREIGN KEY (`id_cancha_id`) REFERENCES `canchas` (`id_cancha`) ON DELETE SET NULL,
  CONSTRAINT `partidos_competitivos_id_localidad_fk` FOREIGN KEY (`id_localidad_id`) REFERENCES `localidades` (`id_localidad`) ON DELETE SET NULL,
  CONSTRAINT `partidos_competitivos_id_creador_fk` FOREIGN KEY (`id_creador_id`) REFERENCES `usuarios` (`id_usuario`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Tabla de invitaciones a equipos
CREATE TABLE IF NOT EXISTS `invitaciones_equipo` (
  `id_invitacion` int NOT NULL AUTO_INCREMENT,
  `id_equipo_id` int NOT NULL,
  `id_usuario_id` int NOT NULL,
  `id_invitador_id` int NOT NULL,
  `mensaje` text,
  `estado` varchar(20) NOT NULL DEFAULT 'pendiente',
  `fecha_invitacion` datetime(6) NOT NULL,
  `fecha_respuesta` datetime(6) DEFAULT NULL,
  PRIMARY KEY (`id_invitacion`),
  UNIQUE KEY `invitaciones_equipo_id_equipo_id_usuario` (`id_equipo_id`, `id_usuario_id`),
  KEY `invitaciones_equipo_id_equipo_id` (`id_equipo_id`),
  KEY `invitaciones_equipo_id_usuario_id` (`id_usuario_id`),
  KEY `invitaciones_equipo_id_invitador_id` (`id_invitador_id`),
  CONSTRAINT `invitaciones_equipo_id_equipo_fk` FOREIGN KEY (`id_equipo_id`) REFERENCES `equipos` (`id_equipo`) ON DELETE CASCADE,
  CONSTRAINT `invitaciones_equipo_id_usuario_fk` FOREIGN KEY (`id_usuario_id`) REFERENCES `usuarios` (`id_usuario`) ON DELETE CASCADE,
  CONSTRAINT `invitaciones_equipo_id_invitador_fk` FOREIGN KEY (`id_invitador_id`) REFERENCES `usuarios` (`id_usuario`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Tabla de estadísticas de jugadores
CREATE TABLE IF NOT EXISTS `estadisticas_jugador` (
  `id_estadistica` int NOT NULL AUTO_INCREMENT,
  `id_partido_id` int NOT NULL,
  `id_usuario_id` int NOT NULL,
  `id_equipo_id` int NOT NULL,
  `goles` int NOT NULL DEFAULT 0,
  `asistencias` int NOT NULL DEFAULT 0,
  `tarjetas_amarillas` int NOT NULL DEFAULT 0,
  `tarjetas_rojas` int NOT NULL DEFAULT 0,
  PRIMARY KEY (`id_estadistica`),
  UNIQUE KEY `estadisticas_jugador_id_partido_id_usuario` (`id_partido_id`, `id_usuario_id`),
  KEY `estadisticas_jugador_id_partido_id` (`id_partido_id`),
  KEY `estadisticas_jugador_id_usuario_id` (`id_usuario_id`),
  KEY `estadisticas_jugador_id_equipo_id` (`id_equipo_id`),
  CONSTRAINT `estadisticas_jugador_id_partido_fk` FOREIGN KEY (`id_partido_id`) REFERENCES `partidos_competitivos` (`id_partido`) ON DELETE CASCADE,
  CONSTRAINT `estadisticas_jugador_id_usuario_fk` FOREIGN KEY (`id_usuario_id`) REFERENCES `usuarios` (`id_usuario`) ON DELETE CASCADE,
  CONSTRAINT `estadisticas_jugador_id_equipo_fk` FOREIGN KEY (`id_equipo_id`) REFERENCES `equipos` (`id_equipo`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
