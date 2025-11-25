-- Crear tabla de mensajes para partidos
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
