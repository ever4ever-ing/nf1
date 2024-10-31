-- Crear la base de datos
CREATE DATABASE IF NOT EXISTS nf1;
USE nf1;

-- Crear tabla User
CREATE TABLE IF NOT EXISTS user (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(20) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    nombre VARCHAR(255) NOT NULL,
    apellido VARCHAR(255) NOT NULL,
    fecha_nacimiento DATE NOT NULL,
    create_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    update_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Crear tabla Match
CREATE TABLE IF NOT EXISTS `match` (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(80) NOT NULL,
    date DATETIME NOT NULL,
    location VARCHAR(255) NOT NULL,
    organizer_id INT NOT NULL,
    create_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (organizer_id) REFERENCES user(id)
);

-- Crear tabla intermedia user_match
CREATE TABLE IF NOT EXISTS user_match (
    user_id INT NOT NULL,
    match_id INT NOT NULL,
    PRIMARY KEY (user_id, match_id),
    FOREIGN KEY (user_id) REFERENCES user(id),
    FOREIGN KEY (match_id) REFERENCES `match`(id)
);

-- Crear tabla Friendship
CREATE TABLE IF NOT EXISTS friendship (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    friend_id INT NOT NULL,
    create_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    update_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user(id),
    FOREIGN KEY (friend_id) REFERENCES user(id)
);

-- Crear tabla Feedback
CREATE TABLE IF NOT EXISTS feedback (
    id INT AUTO_INCREMENT PRIMARY KEY,
    match_player_user_id INT NOT NULL,
    match_player_match_id INT NOT NULL,
    evaluator_id INT NOT NULL,
    talent_score INT NOT NULL,
    committed_score INT NOT NULL,
    friendliness INT NOT NULL,
    create_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (match_player_user_id) REFERENCES user(id),
    FOREIGN KEY (match_player_match_id) REFERENCES `match`(id),
    FOREIGN KEY (evaluator_id) REFERENCES user(id)
);

-- Crear tabla MatchComment
CREATE TABLE IF NOT EXISTS match_comment (
    id INT AUTO_INCREMENT PRIMARY KEY,
    match_id INT NOT NULL,
    user_id INT NOT NULL,
    comment TEXT NOT NULL,
    create_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    update_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (match_id) REFERENCES `match`(id),
    FOREIGN KEY (user_id) REFERENCES user(id)
);
-- Insertar usuarios de prueba (jugadores de la selección chilena 2011)
INSERT INTO user (username, email, password, nombre, apellido, fecha_nacimiento)
VALUES 
('cbravoo', 'cbravoo@example.com', 'hashed_password1', 'Claudio', 'Bravo', '1983-04-13'),
('mriosp', 'mriosp@example.com', 'hashed_password2', 'Mauricio', 'Isla', '1988-06-12'),
('gmedel', 'gmedel@example.com', 'hashed_password3', 'Gary', 'Medel', '1987-08-03'),
('gjaraa', 'gjaraa@example.com', 'hashed_password4', 'Gonzalo', 'Jara', '1985-08-29'),
('mvidal', 'mvidal@example.com', 'hashed_password5', 'Arturo', 'Vidal', '1987-05-22'),
('csanchezz', 'csanchezz@example.com', 'hashed_password6', 'Alexis', 'Sánchez', '1988-12-19'),
('eparedes', 'eparedes@example.com', 'hashed_password7', 'Esteban', 'Paredes', '1980-08-01'),
('jvaldivial', 'jvaldivial@example.com', 'hashed_password8', 'Jorge', 'Valdivia', '1983-10-19'),
('mfernandez', 'mfernandez@example.com', 'hashed_password9', 'Matías', 'Fernández', '1986-05-15'),
('hvargass', 'hvargass@example.com', 'hashed_password10', 'Humberto', 'Suazo', '1981-05-10'),
('jbeausejour', 'jbeausejour@example.com', 'hashed_password11', 'Jean', 'Beausejour', '1984-06-01');

-- Insertar un partido de prueba
INSERT INTO `match` (title, date, location, organizer_id)
VALUES ('Partido amistoso Chile 2011', DATE_ADD(NOW(), INTERVAL 7 DAY), 'Estadio Nacional', 1);

-- Añadir jugadores al partido
INSERT INTO user_match (user_id, match_id) 
VALUES (1, 1), (2, 1), (3, 1), (4, 1), (5, 1), (6, 1), (7, 1), (8, 1), (9, 1), (10, 1), (11, 1);

-- Crear algunas amistades de prueba
INSERT INTO friendship (user_id, friend_id) VALUES (1, 2), (2, 3), (3, 4), (4, 5), (5, 6);

-- Crear algunos feedbacks de prueba
INSERT INTO feedback (match_player_user_id, match_player_match_id, evaluator_id, talent_score, committed_score, friendliness)
VALUES 
(2, 1, 1, 4, 5, 4),
(3, 1, 2, 5, 4, 5),
(4, 1, 3, 3, 5, 4);

-- Crear algunos comentarios de partido de prueba
INSERT INTO match_comment (match_id, user_id, comment)
VALUES 
(1, 6, '¡Gran partido, equipo!'),
(1, 7, 'Excelente juego de todos'),
(1, 8, 'Necesitamos mejorar en el próximo entrenamiento');