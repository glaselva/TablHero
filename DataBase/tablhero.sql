-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Jan 13, 2026 at 03:59 PM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.0.30

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `tablhero`
--

-- --------------------------------------------------------

--
-- Table structure for table `alembic_version`
--

CREATE TABLE `alembic_version` (
  `version_num` varchar(32) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `alembic_version`
--

INSERT INTO `alembic_version` (`version_num`) VALUES
('0d2e3905db58');

-- --------------------------------------------------------

--
-- Table structure for table `eventi`
--

CREATE TABLE `eventi` (
  `id` int(11) NOT NULL,
  `titolo` varchar(100) NOT NULL,
  `descrizione` text DEFAULT NULL,
  `tipo` enum('giochi_tavolo','giochi_ruolo') NOT NULL,
  `data_evento` datetime NOT NULL,
  `max_partecipanti` int(11) DEFAULT NULL,
  `exp_reward` int(11) DEFAULT 50,
  `immagine_url` varchar(255) DEFAULT NULL,
  `creato_da` int(11) DEFAULT NULL,
  `prezzo` decimal(10,2) DEFAULT 0.00,
  `data_creazione` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `eventi`
--

INSERT INTO `eventi` (`id`, `titolo`, `descrizione`, `tipo`, `data_evento`, `max_partecipanti`, `exp_reward`, `immagine_url`, `creato_da`, `prezzo`, `data_creazione`) VALUES
(4, 'La notte e\' tua', '⏳ Firenze ti aspetta. L’evento \"Memento Mori\" di Vampire the Masquerade è ormai alle porte e la caccia sta per cominciare. Non perdere l’occasione di immergerti nell\'avventura e vivere una notte da protagonista.\r\n\r\n\r\nVi aspettiamo qui:\r\n\r\n📅 9 Gennaio 2026 h.19:00 \r\n📍 Spazio25 - Gioia del Colle (BA)', 'giochi_ruolo', '2026-01-09 19:00:00', 15, 50, 'https://i.postimg.cc/0yw6w7WQ/nottetua.jpg', 13, 15.00, '2026-01-13 14:58:32');

-- --------------------------------------------------------

--
-- Table structure for table `partecipazioni`
--

CREATE TABLE `partecipazioni` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `evento_id` int(11) NOT NULL,
  `data_partecipazione` datetime DEFAULT current_timestamp(),
  `exp_guadagnata` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

CREATE TABLE `users` (
  `id` int(11) NOT NULL,
  `nickname` varchar(50) NOT NULL,
  `nome` varchar(50) NOT NULL,
  `cognome` varchar(50) NOT NULL,
  `email` varchar(100) NOT NULL,
  `ruolo` enum('sidekick','tablhero','game_architect','founder') NOT NULL,
  `tabl_exp` int(11) DEFAULT 0,
  `livello` enum('bronzo','argento','oro','platino','diamante') DEFAULT 'bronzo',
  `payment_status` enum('pending','completed','failed') DEFAULT 'pending',
  `stripe_customer_id` varchar(255) DEFAULT NULL,
  `data_registrazione` datetime DEFAULT current_timestamp(),
  `attivo` tinyint(1) DEFAULT 1,
  `ha_pagato` tinyint(1) DEFAULT 0,
  `data_scadenza` datetime DEFAULT NULL,
  `password_hash` varchar(255) NOT NULL DEFAULT '',
  `is_admin` tinyint(1) DEFAULT 0,
  `email_verificata` tinyint(1) DEFAULT NULL,
  `token_verifica` varchar(100) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `users`
--

INSERT INTO `users` (`id`, `nickname`, `nome`, `cognome`, `email`, `ruolo`, `tabl_exp`, `livello`, `payment_status`, `stripe_customer_id`, `data_registrazione`, `attivo`, `ha_pagato`, `data_scadenza`, `password_hash`, `is_admin`, `email_verificata`, `token_verifica`) VALUES
(13, 'giuseppe', 'Giuseppe', 'La Selva', 'giuseppe@tablhero.it', 'founder', 9999, 'diamante', 'pending', NULL, '2026-01-13 08:58:11', 1, 1, NULL, '$2b$12$WkkocOrRmKCpXsImi2oP5eq2g0kfRx43r7H3DVC9pKBXqZku.cjvm', 1, 1, NULL),
(14, 'alessandro', 'Alessandro', 'Palmisano', 'alessandro@tablhero.it', 'founder', 9999, 'diamante', 'pending', NULL, '2026-01-13 08:58:11', 1, 1, NULL, '$2b$12$3nG1KkLS6TxT6WambaKu2OVgJ3YXk.UobFkPLixl7rkIRnL0Cw.2e', 1, 1, NULL),
(15, 'domenico', 'Domenico', 'Longo', 'domenico@tablhero.it', 'founder', 9999, 'diamante', 'pending', NULL, '2026-01-13 08:58:11', 1, 1, NULL, '$2b$12$MUPxJvkhm4r3/XtwWzF/4eIwbtm9wFS80lTa/E0bWgRLj6LUzJmAi', 1, 1, NULL);

--
-- Indexes for dumped tables
--

--
-- Indexes for table `alembic_version`
--
ALTER TABLE `alembic_version`
  ADD PRIMARY KEY (`version_num`);

--
-- Indexes for table `eventi`
--
ALTER TABLE `eventi`
  ADD PRIMARY KEY (`id`),
  ADD KEY `creato_da` (`creato_da`);

--
-- Indexes for table `partecipazioni`
--
ALTER TABLE `partecipazioni`
  ADD PRIMARY KEY (`id`),
  ADD KEY `evento_id` (`evento_id`),
  ADD KEY `user_id` (`user_id`);

--
-- Indexes for table `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `nickname` (`nickname`),
  ADD UNIQUE KEY `email` (`email`),
  ADD UNIQUE KEY `token_verifica` (`token_verifica`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `eventi`
--
ALTER TABLE `eventi`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT for table `partecipazioni`
--
ALTER TABLE `partecipazioni`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT for table `users`
--
ALTER TABLE `users`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=16;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `eventi`
--
ALTER TABLE `eventi`
  ADD CONSTRAINT `eventi_ibfk_1` FOREIGN KEY (`creato_da`) REFERENCES `users` (`id`);

--
-- Constraints for table `partecipazioni`
--
ALTER TABLE `partecipazioni`
  ADD CONSTRAINT `partecipazioni_ibfk_1` FOREIGN KEY (`evento_id`) REFERENCES `eventi` (`id`),
  ADD CONSTRAINT `partecipazioni_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
