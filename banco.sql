-- Execute no MySQL Workbench antes de instalar
CREATE DATABASE IF NOT EXISTS flor_dende_pdv CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS 'flor_dende_user'@'localhost' IDENTIFIED BY 'FlorDende_2026!';
GRANT ALL PRIVILEGES ON flor_dende_pdv.* TO 'flor_dende_user'@'localhost';
FLUSH PRIVILEGES;
SELECT 'Banco criado com sucesso!' AS status;
