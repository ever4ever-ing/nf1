-- Crear tabla de notificaciones
CREATE TABLE IF NOT EXISTS `notificaciones` (
  `id_notificacion` int NOT NULL AUTO_INCREMENT,
  `id_usuario_id` int NOT NULL,
  `id_partido_id` int NOT NULL,
  `tipo` varchar(50) NOT NULL,
  `mensaje` text NOT NULL,
  `leida` tinyint(1) NOT NULL DEFAULT 0,
  `fecha_creacion` datetime(6) NOT NULL,
  `id_usuario_relacionado_id` int DEFAULT NULL,
  `id_mensaje_id` int DEFAULT NULL,
  PRIMARY KEY (`id_notificacion`),
  KEY `notificaciones_id_usuario_id` (`id_usuario_id`),
  KEY `notificaciones_id_partido_id` (`id_partido_id`),
  KEY `notificaciones_id_usuario_relacionado_id` (`id_usuario_relacionado_id`),
  KEY `notificaciones_id_mensaje_id` (`id_mensaje_id`),
  KEY `notificaciones_fecha_creacion` (`fecha_creacion`),
  CONSTRAINT `notificaciones_id_usuario_fk` FOREIGN KEY (`id_usuario_id`) REFERENCES `usuarios` (`id_usuario`) ON DELETE CASCADE,
  CONSTRAINT `notificaciones_id_partido_fk` FOREIGN KEY (`id_partido_id`) REFERENCES `partidos` (`id_partido`) ON DELETE CASCADE,
  CONSTRAINT `notificaciones_id_usuario_relacionado_fk` FOREIGN KEY (`id_usuario_relacionado_id`) REFERENCES `usuarios` (`id_usuario`) ON DELETE CASCADE,
  CONSTRAINT `notificaciones_id_mensaje_fk` FOREIGN KEY (`id_mensaje_id`) REFERENCES `eventos_mensajepartido` (`id_mensaje`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
