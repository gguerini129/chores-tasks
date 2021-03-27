CREATE TABLE `user` (
  `user_id` int(16) NOT NULL AUTO_INCREMENT,
  `username` varchar(32) COLLATE utf8mb4_general_ci NOT NULL,
  `password` varchar(32) COLLATE utf8mb4_general_ci NOT NULL,
  `email` varchar(64) COLLATE utf8mb4_general_ci NOT NULL,
  `first_name` varchar(32) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `last_name` varchar(32) COLLATE utf8mb4_general_ci DEFAULT NULL,
  PRIMARY KEY (`user_id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
