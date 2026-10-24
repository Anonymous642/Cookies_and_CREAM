DROP DATABASE IF EXISTS `web_server`;
CREATE DATABASE IF NOT EXISTS `web_server`;

USE `web_server`;

CREATE TABLE IF NOT EXISTS `users` (
    `user_id` INT(11) NOT NULL AUTO_INCREMENT,
    `username` VARCHAR(64) NOT NULL,
    `password` VARCHAR(64) NOT NULL,
    `firstname` VARCHAR(64) NOT NULL,
    `lastname` VARCHAR(64) NOT NULL,
    PRIMARY KEY (`user_id`)
) DEFAULT CHARSET=latin1;

CREATE TABLE IF NOT EXISTS `sessions` (
    `session_id` VARCHAR(64) NOT NULL,
    `user_id` INT(11) NOT NULL,
    Primary KEY (`session_id`)
) DEFAULT CHARSET=latin1;

CREATE USER 'server'@'172.20.0.3' IDENTIFIED BY 'server_pass';
FLUSH PRIVILEGES;
GRANT ALL ON web_server.* TO 'server'@'172.20.0.3';
FLUSH PRIVILEGES;
