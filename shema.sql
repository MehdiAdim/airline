DROP DATABASE 'airline';
CREATE DATABASE  IF NOT EXISTS `airline` /*!40100 DEFAULT CHARACTER SET utf8 */;
USE `airline`;
-- MySQL dump 10.13  Distrib 8.0.12, for macos10.13 (x86_64)
--
-- Host: localhost    Database: airline
-- ------------------------------------------------------
-- Server version	8.0.12

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
 SET NAMES utf8 ;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `aircrafts`
--

DROP TABLE IF EXISTS `aircrafts`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
 SET character_set_client = utf8mb4 ;
CREATE TABLE `aircrafts` (
  `aircraftID` int(11) NOT NULL AUTO_INCREMENT,
  `immatriculation` varchar(30) NOT NULL,
  `type` varchar(10) NOT NULL,
  `seats` int(11) NOT NULL,
  PRIMARY KEY (`aircraftID`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `airports`
--

DROP TABLE IF EXISTS `airports`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
 SET character_set_client = utf8mb4 ;
CREATE TABLE `airports` (
  `airportID` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `code` varchar(3) NOT NULL,
  `city` varchar(100) NOT NULL,
  PRIMARY KEY (`airportID`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `clients`
--

DROP TABLE IF EXISTS `clients`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
 SET character_set_client = utf8mb4 ;
CREATE TABLE `clients` (
  `clientID` int(11) NOT NULL AUTO_INCREMENT,
  `surname` varchar(45) NOT NULL,
  `firstname` varchar(45) NOT NULL,
  `address` varchar(300) NOT NULL,
  `email` varchar(300) NOT NULL,
  `password` varchar(45) NOT NULL,
  `username` varchar(45) NOT NULL,
  PRIMARY KEY (`clientID`),
  UNIQUE KEY `email_UNIQUE` (`email`),
  UNIQUE KEY `username_UNIQUE` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `departures`
--

DROP TABLE IF EXISTS `departures`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
 SET character_set_client = utf8mb4 ;
CREATE TABLE `departures` (
  `departureID` int(11) NOT NULL AUTO_INCREMENT,
  `departure_date` date NOT NULL,
  `free_seats` int(11) DEFAULT NULL,
  `sold_seats` int(11) DEFAULT NULL,
  `flightID` int(11) NOT NULL,
  `pilot1ID` int(11) NOT NULL,
  `pilot2ID` int(11) NOT NULL,
  `crew_member1ID` int(11) NOT NULL,
  `crew_member2ID` int(11) NOT NULL,
  PRIMARY KEY (`departureID`),
  KEY `fk_departs_vols1_idx` (`flightID`),
  KEY `fk_departs_pilots1_idx` (`pilot1ID`),
  KEY `fk_departs_pilots2_idx` (`pilot2ID`),
  KEY `fk_departs_crew_members1_idx` (`crew_member1ID`),
  KEY `fk_departs_crew_members2_idx` (`crew_member2ID`),
  CONSTRAINT `fk_departs_crew_members1` FOREIGN KEY (`crew_member1ID`) REFERENCES `employees` (`employeeid`) ON DELETE CASCADE,
  CONSTRAINT `fk_departs_crew_members2` FOREIGN KEY (`crew_member2ID`) REFERENCES `employees` (`employeeid`) ON DELETE CASCADE,
  CONSTRAINT `fk_departs_pilots1` FOREIGN KEY (`pilot1ID`) REFERENCES `employees` (`employeeid`)ON DELETE CASCADE,
  CONSTRAINT `fk_departs_pilots2` FOREIGN KEY (`pilot2ID`) REFERENCES `employees` (`employeeid`)ON DELETE CASCADE,
  CONSTRAINT `fk_departs_vols1` FOREIGN KEY (`flightID`) REFERENCES `flights` (`flightid`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `employees`
--

DROP TABLE IF EXISTS `employees`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
 SET character_set_client = utf8mb4 ;
CREATE TABLE `employees` (
  `employeeID` int(11) NOT NULL AUTO_INCREMENT,
  `salary` decimal(9,2) NOT NULL,
  `address` varchar(500) NOT NULL,
  `firstname` varchar(45) NOT NULL,
  `surname` varchar(45) NOT NULL,
  `flight_hours` decimal(9,2) NOT NULL,
  `social_security_number` int(11) NOT NULL,
  `roleID` int(11) NOT NULL,
  PRIMARY KEY (`employeeID`),
  KEY `fk_role_idx` (`roleID`),
  CONSTRAINT `fk_role` FOREIGN KEY (`roleID`) REFERENCES `role` (`roleid`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `flights`
--

DROP TABLE IF EXISTS `flights`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
 SET character_set_client = utf8mb4 ;
CREATE TABLE `flights` (
  `flightID` int(11) NOT NULL AUTO_INCREMENT,
  `date1` date NOT NULL,
  `date2` date NOT NULL,
  `departure_time` time NOT NULL,
  `arrival_time` time NOT NULL,
  `aircraftID` int(11) NOT NULL,
  `linkID` int(11) NOT NULL,
  `base_price` decimal(10,0) NOT NULL,
  `day_plus_1` tinyint(4) NOT NULL,
  PRIMARY KEY (`flightID`),
  KEY `fk_vols_appareils1_idx` (`aircraftID`),
  KEY `fk_vols_liaisons1_idx` (`linkID`),
  CONSTRAINT `fk_vols_appareils1` FOREIGN KEY (`aircraftID`) REFERENCES `aircrafts` (`aircraftid`) ON DELETE CASCADE,
  CONSTRAINT `fk_vols_liaisons1` FOREIGN KEY (`linkID`) REFERENCES `links` (`linkid`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `links`
--

DROP TABLE IF EXISTS `links`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
 SET character_set_client = utf8mb4 ;
CREATE TABLE `links` (
  `linkID` int(11) NOT NULL AUTO_INCREMENT,
  `departure_airportID` int(11) NOT NULL,
  `arrival_airportID` int(11) NOT NULL,
  PRIMARY KEY (`linkID`),
  KEY `fk_liaisons_airports1_idx` (`departure_airportID`),
  KEY `fk_liaisons_airports2_idx` (`arrival_airportID`),
  CONSTRAINT `fk_liaisons_airports1` FOREIGN KEY (`departure_airportID`) REFERENCES `airports` (`airportid`)ON DELETE CASCADE,
  CONSTRAINT `fk_liaisons_airports2` FOREIGN KEY (`arrival_airportID`) REFERENCES `airports` (`airportid`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `role`
--

DROP TABLE IF EXISTS `role`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
 SET character_set_client = utf8mb4 ;
CREATE TABLE `role` (
  `roleID` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(45) NOT NULL,
  PRIMARY KEY (`roleID`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `tickets`
--

DROP TABLE IF EXISTS `tickets`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
 SET character_set_client = utf8mb4 ;
CREATE TABLE `tickets` (
  `ticketID` int(11) NOT NULL AUTO_INCREMENT,
  `date_of_issue` datetime NOT NULL,
  `price` decimal(9,2) NOT NULL,
  `departureID` int(11) NOT NULL,
  `clientID` int(11) NOT NULL,
  PRIMARY KEY (`ticketID`),
  KEY `fk_tickets_departs1_idx` (`departureID`),
  KEY `fk_tickets_clients1_idx` (`clientID`),
  CONSTRAINT `client` FOREIGN KEY (`clientID`) REFERENCES `clients` (`clientid`) ON DELETE CASCADE,
  CONSTRAINT `departure` FOREIGN KEY (`departureID`) REFERENCES `departures` (`departureid`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 TRIGGER `tickets_AFTER_INSERT` AFTER INSERT ON `tickets` FOR EACH ROW BEGIN
	UPDATE `airline`.`departures`
	SET free_seats = free_seats - 1, sold_seats = sold_seats + 1
    WHERE departureID = NEW.departureID;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 TRIGGER `tickets_AFTER_DELETE` AFTER DELETE ON `tickets` FOR EACH ROW BEGIN
	UPDATE `airline`.`departures`
	SET free_seats = free_seats + 1, sold_seats = sold_seats - 1
    WHERE departureID = OLD.departureID;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2018-11-30 16:59:13
