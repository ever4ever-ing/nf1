-- Agregar campos de perfil y ranking a la tabla usuarios
ALTER TABLE `usuarios` 
ADD COLUMN `foto_perfil` varchar(100) DEFAULT NULL AFTER `is_admin`,
ADD COLUMN `fecha_nacimiento` date DEFAULT NULL AFTER `foto_perfil`,
ADD COLUMN `hobbies` text DEFAULT NULL AFTER `fecha_nacimiento`,
ADD COLUMN `biografia` text DEFAULT NULL AFTER `hobbies`,
ADD COLUMN `puntos_friendly` int NOT NULL DEFAULT 0 AFTER `biografia`;
