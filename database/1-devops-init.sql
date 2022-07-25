-- MySQL dump 10.13  Distrib 5.7.36, for Linux (x86_64)
--
-- Host: mysql-service    Database: devops
-- ------------------------------------------------------
-- Server version	5.7.36

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Current Database: `devops`
--

CREATE DATABASE /*!32312 IF NOT EXISTS*/ `devops` /*!40100 DEFAULT CHARACTER SET utf8mb4 */;

USE `devops`;

--
-- Table structure for table `auth_group`
--

DROP TABLE IF EXISTS `auth_group`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_group` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(150) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_group`
--

LOCK TABLES `auth_group` WRITE;
/*!40000 ALTER TABLE `auth_group` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_group` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_group_permissions`
--

DROP TABLE IF EXISTS `auth_group_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_group_permissions` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `group_id` int(11) NOT NULL,
  `permission_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_group_permissions_group_id_permission_id_0cd325b0_uniq` (`group_id`,`permission_id`),
  KEY `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` (`permission_id`),
  CONSTRAINT `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `auth_group_permissions_group_id_b120cbf9_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_group_permissions`
--

LOCK TABLES `auth_group_permissions` WRITE;
/*!40000 ALTER TABLE `auth_group_permissions` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_group_permissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_permission`
--

DROP TABLE IF EXISTS `auth_permission`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_permission` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `content_type_id` int(11) NOT NULL,
  `codename` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_permission_content_type_id_codename_01ab375a_uniq` (`content_type_id`,`codename`),
  CONSTRAINT `auth_permission_content_type_id_2f476e4b_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=69 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_permission`
--

LOCK TABLES `auth_permission` WRITE;
/*!40000 ALTER TABLE `auth_permission` DISABLE KEYS */;
INSERT INTO `auth_permission` VALUES (1,'Can add permission',1,'add_permission'),(2,'Can change permission',1,'change_permission'),(3,'Can delete permission',1,'delete_permission'),(4,'Can view permission',1,'view_permission'),(5,'Can add group',2,'add_group'),(6,'Can change group',2,'change_group'),(7,'Can delete group',2,'delete_group'),(8,'Can view group',2,'view_group'),(9,'Can add user',3,'add_user'),(10,'Can change user',3,'change_user'),(11,'Can delete user',3,'delete_user'),(12,'Can view user',3,'view_user'),(13,'Can add content type',4,'add_contenttype'),(14,'Can change content type',4,'change_contenttype'),(15,'Can delete content type',4,'delete_contenttype'),(16,'Can view content type',4,'view_contenttype'),(17,'Can add session',5,'add_session'),(18,'Can change session',5,'change_session'),(19,'Can delete session',5,'delete_session'),(20,'Can view session',5,'view_session'),(21,'Can add 主机组',6,'add_hostgroup'),(22,'Can change 主机组',6,'change_hostgroup'),(23,'Can delete 主机组',6,'delete_hostgroup'),(24,'Can view 主机组',6,'view_hostgroup'),(25,'Can add 主机账户',7,'add_remoteuser'),(26,'Can change 主机账户',7,'change_remoteuser'),(27,'Can delete 主机账户',7,'delete_remoteuser'),(28,'Can view 主机账户',7,'view_remoteuser'),(29,'Can add 远程主机',8,'add_remoteuserbindhost'),(30,'Can change 远程主机',8,'change_remoteuserbindhost'),(31,'Can delete 远程主机',8,'delete_remoteuserbindhost'),(32,'Can view 远程主机',8,'view_remoteuserbindhost'),(33,'Can add 主机详细',9,'add_serverdetail'),(34,'Can change 主机详细',9,'change_serverdetail'),(35,'Can delete 主机详细',9,'delete_serverdetail'),(36,'Can view 主机详细',9,'view_serverdetail'),(37,'Can add 用户组',10,'add_group'),(38,'Can change 用户组',10,'change_group'),(39,'Can delete 用户组',10,'delete_group'),(40,'Can view 用户组',10,'view_group'),(41,'Can add 用户日志',11,'add_loginlog'),(42,'Can change 用户日志',11,'change_loginlog'),(43,'Can delete 用户日志',11,'delete_loginlog'),(44,'Can view 用户日志',11,'view_loginlog'),(45,'Can add 权限',12,'add_permission'),(46,'Can change 权限',12,'change_permission'),(47,'Can delete 权限',12,'delete_permission'),(48,'Can view 权限',12,'view_permission'),(49,'Can add 用户',13,'add_user'),(50,'Can change 用户',13,'change_user'),(51,'Can delete 用户',13,'delete_user'),(52,'Can view 用户',13,'view_user'),(53,'Can add 在线会话日志',14,'add_terminallog'),(54,'Can change 在线会话日志',14,'change_terminallog'),(55,'Can delete 在线会话日志',14,'delete_terminallog'),(56,'Can view 在线会话日志',14,'view_terminallog'),(57,'Can add 在线会话',15,'add_terminalsession'),(58,'Can change 在线会话',15,'change_terminalsession'),(59,'Can delete 在线会话',15,'delete_terminalsession'),(60,'Can view 在线会话',15,'view_terminalsession'),(61,'Can add 批量日志',16,'add_batchcmdlog'),(62,'Can change 批量日志',16,'change_batchcmdlog'),(63,'Can delete 批量日志',16,'delete_batchcmdlog'),(64,'Can view 批量日志',16,'view_batchcmdlog'),(65,'Can add 调度主机',17,'add_schedulerhost'),(66,'Can change 调度主机',17,'change_schedulerhost'),(67,'Can delete 调度主机',17,'delete_schedulerhost'),(68,'Can view 调度主机',17,'view_schedulerhost');
/*!40000 ALTER TABLE `auth_permission` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_user`
--

DROP TABLE IF EXISTS `auth_user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_user` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `password` varchar(128) NOT NULL,
  `last_login` datetime(6) DEFAULT NULL,
  `is_superuser` tinyint(1) NOT NULL,
  `username` varchar(150) NOT NULL,
  `first_name` varchar(30) NOT NULL,
  `last_name` varchar(150) NOT NULL,
  `email` varchar(254) NOT NULL,
  `is_staff` tinyint(1) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `date_joined` datetime(6) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_user`
--

LOCK TABLES `auth_user` WRITE;
/*!40000 ALTER TABLE `auth_user` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_user` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_user_groups`
--

DROP TABLE IF EXISTS `auth_user_groups`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_user_groups` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `group_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_user_groups_user_id_group_id_94350c0c_uniq` (`user_id`,`group_id`),
  KEY `auth_user_groups_group_id_97559544_fk_auth_group_id` (`group_id`),
  CONSTRAINT `auth_user_groups_group_id_97559544_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`),
  CONSTRAINT `auth_user_groups_user_id_6a12ed8b_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_user_groups`
--

LOCK TABLES `auth_user_groups` WRITE;
/*!40000 ALTER TABLE `auth_user_groups` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_user_groups` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_user_user_permissions`
--

DROP TABLE IF EXISTS `auth_user_user_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_user_user_permissions` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `permission_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_user_user_permissions_user_id_permission_id_14a6b632_uniq` (`user_id`,`permission_id`),
  KEY `auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm` (`permission_id`),
  CONSTRAINT `auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `auth_user_user_permissions_user_id_a95ead1b_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_user_user_permissions`
--

LOCK TABLES `auth_user_user_permissions` WRITE;
/*!40000 ALTER TABLE `auth_user_user_permissions` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_user_user_permissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `batch_batchcmdlog`
--

DROP TABLE IF EXISTS `batch_batchcmdlog`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `batch_batchcmdlog` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user` varchar(64) NOT NULL,
  `hosts` longtext NOT NULL,
  `cmd` longtext,
  `type` smallint(6) NOT NULL,
  `script` varchar(128) DEFAULT NULL,
  `detail` varchar(128) DEFAULT NULL,
  `address` char(39) DEFAULT NULL,
  `useragent` varchar(512) DEFAULT NULL,
  `start_time` datetime(6) NOT NULL,
  `create_time` datetime(6) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `batch_batchcmdlog`
--

LOCK TABLES `batch_batchcmdlog` WRITE;
/*!40000 ALTER TABLE `batch_batchcmdlog` DISABLE KEYS */;
/*!40000 ALTER TABLE `batch_batchcmdlog` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_content_type`
--

DROP TABLE IF EXISTS `django_content_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `django_content_type` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `app_label` varchar(100) NOT NULL,
  `model` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `django_content_type_app_label_model_76bd3d3b_uniq` (`app_label`,`model`)
) ENGINE=InnoDB AUTO_INCREMENT=18 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_content_type`
--

LOCK TABLES `django_content_type` WRITE;
/*!40000 ALTER TABLE `django_content_type` DISABLE KEYS */;
INSERT INTO `django_content_type` VALUES (2,'auth','group'),(1,'auth','permission'),(3,'auth','user'),(16,'batch','batchcmdlog'),(4,'contenttypes','contenttype'),(17,'scheduler','schedulerhost'),(6,'server','hostgroup'),(7,'server','remoteuser'),(8,'server','remoteuserbindhost'),(9,'server','serverdetail'),(5,'sessions','session'),(10,'user','group'),(11,'user','loginlog'),(12,'user','permission'),(13,'user','user'),(14,'webssh','terminallog'),(15,'webssh','terminalsession');
/*!40000 ALTER TABLE `django_content_type` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_migrations`
--

DROP TABLE IF EXISTS `django_migrations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `django_migrations` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `app` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `applied` datetime(6) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=21 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_migrations`
--

LOCK TABLES `django_migrations` WRITE;
/*!40000 ALTER TABLE `django_migrations` DISABLE KEYS */;
INSERT INTO `django_migrations` VALUES (1,'contenttypes','0001_initial','2021-12-10 14:12:02.400190'),(2,'contenttypes','0002_remove_content_type_name','2021-12-10 14:12:02.672512'),(3,'auth','0001_initial','2021-12-10 14:12:03.177634'),(4,'auth','0002_alter_permission_name_max_length','2021-12-10 14:12:04.779491'),(5,'auth','0003_alter_user_email_max_length','2021-12-10 14:12:04.811719'),(6,'auth','0004_alter_user_username_opts','2021-12-10 14:12:04.825087'),(7,'auth','0005_alter_user_last_login_null','2021-12-10 14:12:04.951017'),(8,'auth','0006_require_contenttypes_0002','2021-12-10 14:12:04.961438'),(9,'auth','0007_alter_validators_add_error_messages','2021-12-10 14:12:04.976898'),(10,'auth','0008_alter_user_username_max_length','2021-12-10 14:12:05.142635'),(11,'auth','0009_alter_user_last_name_max_length','2021-12-10 14:12:05.322084'),(12,'auth','0010_alter_group_name_max_length','2021-12-10 14:12:05.356377'),(13,'auth','0011_update_proxy_permissions','2021-12-10 14:12:05.372579'),(14,'batch','0001_initial','2021-12-10 14:12:05.456504'),(15,'scheduler','0001_initial','2021-12-10 14:12:05.533007'),(16,'server','0001_initial','2021-12-10 14:12:06.020276'),(17,'user','0001_initial','2021-12-10 14:12:07.590745'),(18,'server','0002_auto_20211210_1412','2021-12-10 14:12:09.943222'),(19,'sessions','0001_initial','2021-12-10 14:12:10.209022'),(20,'webssh','0001_initial','2021-12-10 14:12:10.429973');
/*!40000 ALTER TABLE `django_migrations` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_session`
--

DROP TABLE IF EXISTS `django_session`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `django_session` (
  `session_key` varchar(40) NOT NULL,
  `session_data` longtext NOT NULL,
  `expire_date` datetime(6) NOT NULL,
  PRIMARY KEY (`session_key`),
  KEY `django_session_expire_date_a5c62663` (`expire_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_session`
--

LOCK TABLES `django_session` WRITE;
/*!40000 ALTER TABLE `django_session` DISABLE KEYS */;
/*!40000 ALTER TABLE `django_session` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `scheduler_schedulerhost`
--

DROP TABLE IF EXISTS `scheduler_schedulerhost`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `scheduler_schedulerhost` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `hostname` varchar(128) DEFAULT NULL,
  `ip` char(39) NOT NULL,
  `protocol` smallint(6) NOT NULL,
  `port` smallint(6) NOT NULL,
  `token` varchar(512) NOT NULL,
  `status` tinyint(1) NOT NULL,
  `cron` int(11) NOT NULL,
  `interval` int(11) NOT NULL,
  `date` int(11) NOT NULL,
  `executed` int(11) NOT NULL,
  `failed` int(11) NOT NULL,
  `memo` longtext,
  `update_time` datetime(6) DEFAULT NULL,
  `create_time` datetime(6) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `scheduler_schedulerhost_ip_port_05e61db0_uniq` (`ip`,`port`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `scheduler_schedulerhost`
--

LOCK TABLES `scheduler_schedulerhost` WRITE;
/*!40000 ALTER TABLE `scheduler_schedulerhost` DISABLE KEYS */;
/*!40000 ALTER TABLE `scheduler_schedulerhost` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `server_hostgroup`
--

DROP TABLE IF EXISTS `server_hostgroup`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `server_hostgroup` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `group_name` varchar(128) NOT NULL,
  `memo` longtext,
  `create_time` datetime(6) NOT NULL,
  `user_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `server_hostgroup_group_name_user_id_529f90b8_uniq` (`group_name`,`user_id`),
  KEY `server_hostgroup_user_id_fb2f2a35_fk_user_user_id` (`user_id`),
  CONSTRAINT `server_hostgroup_user_id_fb2f2a35_fk_user_user_id` FOREIGN KEY (`user_id`) REFERENCES `user_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `server_hostgroup`
--

LOCK TABLES `server_hostgroup` WRITE;
/*!40000 ALTER TABLE `server_hostgroup` DISABLE KEYS */;
/*!40000 ALTER TABLE `server_hostgroup` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `server_remoteuser`
--

DROP TABLE IF EXISTS `server_remoteuser`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `server_remoteuser` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(128) NOT NULL,
  `username` varchar(128) NOT NULL,
  `password` varchar(512) NOT NULL,
  `domain` varchar(256) DEFAULT NULL,
  `enabled` tinyint(1) NOT NULL,
  `superusername` varchar(128) DEFAULT NULL,
  `superpassword` varchar(512) DEFAULT NULL,
  `memo` longtext,
  `create_time` datetime(6) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `server_remoteuser`
--

LOCK TABLES `server_remoteuser` WRITE;
/*!40000 ALTER TABLE `server_remoteuser` DISABLE KEYS */;
/*!40000 ALTER TABLE `server_remoteuser` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `server_remoteuserbindhost`
--

DROP TABLE IF EXISTS `server_remoteuserbindhost`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `server_remoteuserbindhost` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `hostname` varchar(128) NOT NULL,
  `type` smallint(6) NOT NULL,
  `ip` char(39) NOT NULL,
  `wip` char(39) DEFAULT NULL,
  `protocol` smallint(6) NOT NULL,
  `env` smallint(6) NOT NULL,
  `port` smallint(6) NOT NULL,
  `release` varchar(255) NOT NULL,
  `platform` smallint(6) NOT NULL,
  `security` varchar(32) DEFAULT NULL,
  `memo` longtext,
  `enabled` tinyint(1) NOT NULL,
  `create_time` datetime(6) NOT NULL,
  `remote_user_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `hostname` (`hostname`),
  UNIQUE KEY `server_remoteuserbindhos_ip_protocol_port_remote__43a07529_uniq` (`ip`,`protocol`,`port`,`remote_user_id`),
  KEY `server_remoteuserbin_remote_user_id_99ea1334_fk_server_re` (`remote_user_id`),
  CONSTRAINT `server_remoteuserbin_remote_user_id_99ea1334_fk_server_re` FOREIGN KEY (`remote_user_id`) REFERENCES `server_remoteuser` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `server_remoteuserbindhost`
--

LOCK TABLES `server_remoteuserbindhost` WRITE;
/*!40000 ALTER TABLE `server_remoteuserbindhost` DISABLE KEYS */;
/*!40000 ALTER TABLE `server_remoteuserbindhost` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `server_remoteuserbindhost_host_group`
--

DROP TABLE IF EXISTS `server_remoteuserbindhost_host_group`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `server_remoteuserbindhost_host_group` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `remoteuserbindhost_id` int(11) NOT NULL,
  `hostgroup_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `server_remoteuserbindhos_remoteuserbindhost_id_ho_e2fa1d83_uniq` (`remoteuserbindhost_id`,`hostgroup_id`),
  KEY `server_remoteuserbin_hostgroup_id_c72cf47f_fk_server_ho` (`hostgroup_id`),
  CONSTRAINT `server_remoteuserbin_hostgroup_id_c72cf47f_fk_server_ho` FOREIGN KEY (`hostgroup_id`) REFERENCES `server_hostgroup` (`id`),
  CONSTRAINT `server_remoteuserbin_remoteuserbindhost_i_45428e4e_fk_server_re` FOREIGN KEY (`remoteuserbindhost_id`) REFERENCES `server_remoteuserbindhost` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `server_remoteuserbindhost_host_group`
--

LOCK TABLES `server_remoteuserbindhost_host_group` WRITE;
/*!40000 ALTER TABLE `server_remoteuserbindhost_host_group` DISABLE KEYS */;
/*!40000 ALTER TABLE `server_remoteuserbindhost_host_group` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `server_serverdetail`
--

DROP TABLE IF EXISTS `server_serverdetail`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `server_serverdetail` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `cpu_model` varchar(128) DEFAULT NULL,
  `cpu_number` smallint(6) DEFAULT NULL,
  `vcpu_number` smallint(6) DEFAULT NULL,
  `disk_total` varchar(16) DEFAULT NULL,
  `ram_total` smallint(6) DEFAULT NULL,
  `swap_total` smallint(6) DEFAULT NULL,
  `kernel` varchar(128) DEFAULT NULL,
  `system` varchar(128) DEFAULT NULL,
  `filesystems` longtext,
  `interfaces` longtext,
  `server_model` varchar(128) DEFAULT NULL,
  `server_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `server_id` (`server_id`),
  CONSTRAINT `server_serverdetail_server_id_742ec3a8_fk_server_re` FOREIGN KEY (`server_id`) REFERENCES `server_remoteuserbindhost` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `server_serverdetail`
--

LOCK TABLES `server_serverdetail` WRITE;
/*!40000 ALTER TABLE `server_serverdetail` DISABLE KEYS */;
/*!40000 ALTER TABLE `server_serverdetail` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user_group`
--

DROP TABLE IF EXISTS `user_group`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `user_group` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `group_name` varchar(128) NOT NULL,
  `memo` longtext,
  `create_time` datetime(6) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `group_name` (`group_name`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user_group`
--

LOCK TABLES `user_group` WRITE;
/*!40000 ALTER TABLE `user_group` DISABLE KEYS */;
/*!40000 ALTER TABLE `user_group` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user_group_permission`
--

DROP TABLE IF EXISTS `user_group_permission`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `user_group_permission` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `group_id` int(11) NOT NULL,
  `permission_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_group_permission_group_id_permission_id_a98dbad2_uniq` (`group_id`,`permission_id`),
  KEY `user_group_permissio_permission_id_18e9ae70_fk_user_perm` (`permission_id`),
  CONSTRAINT `user_group_permissio_permission_id_18e9ae70_fk_user_perm` FOREIGN KEY (`permission_id`) REFERENCES `user_permission` (`id`),
  CONSTRAINT `user_group_permission_group_id_c223ed5c_fk_user_group_id` FOREIGN KEY (`group_id`) REFERENCES `user_group` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=50 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user_group_permission`
--

LOCK TABLES `user_group_permission` WRITE;
/*!40000 ALTER TABLE `user_group_permission` DISABLE KEYS */;
/*!40000 ALTER TABLE `user_group_permission` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user_group_remote_user_bind_hosts`
--

DROP TABLE IF EXISTS `user_group_remote_user_bind_hosts`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `user_group_remote_user_bind_hosts` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `group_id` int(11) NOT NULL,
  `remoteuserbindhost_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_group_remote_user_b_group_id_remoteuserbindh_5f9f2469_uniq` (`group_id`,`remoteuserbindhost_id`),
  KEY `user_group_remote_us_remoteuserbindhost_i_4252c8c9_fk_server_re` (`remoteuserbindhost_id`),
  CONSTRAINT `user_group_remote_us_group_id_8bf7ba65_fk_user_grou` FOREIGN KEY (`group_id`) REFERENCES `user_group` (`id`),
  CONSTRAINT `user_group_remote_us_remoteuserbindhost_i_4252c8c9_fk_server_re` FOREIGN KEY (`remoteuserbindhost_id`) REFERENCES `server_remoteuserbindhost` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user_group_remote_user_bind_hosts`
--

LOCK TABLES `user_group_remote_user_bind_hosts` WRITE;
/*!40000 ALTER TABLE `user_group_remote_user_bind_hosts` DISABLE KEYS */;
/*!40000 ALTER TABLE `user_group_remote_user_bind_hosts` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user_loginlog`
--

DROP TABLE IF EXISTS `user_loginlog`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `user_loginlog` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user` varchar(64) DEFAULT NULL,
  `event_type` smallint(6) NOT NULL,
  `detail` longtext NOT NULL,
  `address` char(39) DEFAULT NULL,
  `useragent` varchar(512) DEFAULT NULL,
  `create_time` datetime(6) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user_loginlog`
--

LOCK TABLES `user_loginlog` WRITE;
/*!40000 ALTER TABLE `user_loginlog` DISABLE KEYS */;
/*!40000 ALTER TABLE `user_loginlog` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user_permission`
--

DROP TABLE IF EXISTS `user_permission`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `user_permission` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `title` varchar(128) NOT NULL,
  `url` varchar(256) DEFAULT NULL,
  `icon` varchar(128) DEFAULT NULL,
  `menu` varchar(128) DEFAULT NULL,
  `men_icon` varchar(128) DEFAULT NULL,
  `is_button` tinyint(1) NOT NULL,
  `order` smallint(6) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `title` (`title`)
) ENGINE=InnoDB AUTO_INCREMENT=53 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user_permission`
--

LOCK TABLES `user_permission` WRITE;
/*!40000 ALTER TABLE `user_permission` DISABLE KEYS */;
INSERT INTO `user_permission` VALUES (1,'仪表盘','/server/','<i class=\"nav-icon fas fa-tachometer-alt fa-xs\"></i>',NULL,NULL,0,1),(2,'用户','/user/users/',NULL,'用户管理','<i class=\"nav-icon fas fa-user fa-xs\"></i>',0,2),(3,'组','/user/groups/',NULL,'用户管理','<i class=\"nav-icon fas fa-user fa-xs\"></i>',0,3),(4,'主机','/server/hosts/',NULL,'主机管理','<i class=\"nav-icon fas fa-copy fa-xs\"></i>',0,4),(5,'主机组','/server/groups/',NULL,'主机管理','<i class=\"nav-icon fas fa-copy fa-xs\"></i>',0,5),(6,'远程用户','/server/users/',NULL,'主机管理','<i class=\"nav-icon fas fa-copy fa-xs\"></i>',0,6),(7,'终端登录','/webssh/hosts/',NULL,'远程终端','<i class=\"nav-icon fas fa-coffee fa-xs\"></i>',0,7),(8,'在线终端','/webssh/sessions/',NULL,'远程终端','<i class=\"nav-icon fas fa-coffee fa-xs\"></i>',0,8),(9,'批量命令','/batch/cmd/,/api/batch/get/hosts/,/ws/cmd/',NULL,'批量处理','<i class=\"nav-icon fas fa-align-justify fa-xs\"></i>',0,9),(10,'批量脚本','/batch/script/,/api/batch/get/hosts/,/ws/script/',NULL,'批量处理','<i class=\"nav-icon fas fa-align-justify fa-xs\"></i>',0,10),(11,'上传文件','/batch/file/,/api/batch/upload/,/ws/file/',NULL,'批量处理','<i class=\"nav-icon fas fa-align-justify fa-xs\"></i>',0,11),(12,'module','/batch/module/,/ws/module/',NULL,'批量处理','<i class=\"nav-icon fas fa-align-justify fa-xs\"></i>',0,12),(13,'playbook','/batch/playbook/,/ws/playbook/',NULL,'批量处理','<i class=\"nav-icon fas fa-align-justify fa-xs\"></i>',0,13),(14,'操作日志','/user/logs/,/api/user/logs/',NULL,'日志审计','<i class=\"nav-icon fas fa-history fa-xs\"></i>',0,14),(15,'终端日志','/webssh/logs/,/api/webssh/logs/',NULL,'日志审计','<i class=\"nav-icon fas fa-history fa-xs\"></i>',0,15),(16,'批量日志','/batch/logs/,/api/batch/logs/',NULL,'日志审计','<i class=\"nav-icon fas fa-history fa-xs\"></i>',0,16),(17,'用户详细','/user/user/(?P<user_id>[0-9]+)/',NULL,'用户管理',NULL,1,123),(18,'用户编辑','/user/user/(?P<user_id>[0-9]+)/edit/,/api/user/user/update/',NULL,'用户管理',NULL,1,123),(19,'用户删除','/api/user/user/delete/',NULL,'用户管理',NULL,1,123),(20,'用户添加','/user/user/add/,/api/user/user/add/',NULL,'用户管理',NULL,1,123),(21,'组详细','/user/group/(?P<group_id>[0-9]+)/',NULL,'用户管理',NULL,1,123),(22,'组编辑','/user/group/(?P<group_id>[0-9]+)/edit/,/api/user/group/update/',NULL,'用户管理',NULL,1,123),(23,'组删除','/api/user/group/delete/',NULL,'用户管理',NULL,1,123),(24,'组添加','/user/group/add/,/api/user/group/add/',NULL,'用户管理',NULL,1,123),(25,'主机详细','/server/host/(?P<host_id>[0-9]+)/',NULL,'主机管理',NULL,1,123),(26,'主机编辑','/server/host/(?P<host_id>[0-9]+)/edit/,/api/server/host/update/',NULL,'主机管理',NULL,1,123),(27,'主机删除','/api/server/host/delete/',NULL,'主机管理',NULL,1,123),(28,'主机添加','/server/host/add/,/api/server/host/add/',NULL,'主机管理',NULL,1,123),(29,'主机更新','/api/server/host/update/info/',NULL,'主机管理',NULL,1,123),(30,'主机组详细','/server/group/(?P<group_id>[0-9]+)/',NULL,'主机管理',NULL,1,123),(31,'主机组编辑','/server/group/(?P<group_id>[0-9]+)/edit/,/api/server/group/update/',NULL,'主机管理',NULL,1,123),(32,'主机组删除','/api/server/group/delete/',NULL,'主机管理',NULL,1,123),(33,'主机组添加','/server/group/add/,/api/server/group/add/',NULL,'主机管理',NULL,1,123),(34,'远程用户详细','/server/user/(?P<user_id>[0-9]+)/',NULL,'主机管理',NULL,1,123),(35,'远程用户编辑','/server/user/(?P<user_id>[0-9]+)/edit/,/api/server/user/update/',NULL,'主机管理',NULL,1,123),(36,'远程用户删除','/api/server/user/delete/',NULL,'主机管理',NULL,1,123),(37,'远程用户添加','/server/user/add/,/api/server/user/add/',NULL,'主机管理',NULL,1,123),(38,'webssh终端','/webssh/terminal/,/ws/webssh/',NULL,'远程终端',NULL,1,123),(39,'客户端ssh','/webssh/terminal/cli/',NULL,'远程终端',NULL,1,123),(40,'客户端sftp','/webssh/terminal/cli/sftp',NULL,'远程终端',NULL,1,123),(41,'webtelnet终端','/webtelnet/terminal/,/ws/webtelnet/',NULL,'远程终端',NULL,1,123),(42,'webguacamole终端','/webguacamole/terminal/,/ws/webguacamole/',NULL,'远程终端',NULL,1,123),(43,'终端会话查看','/webssh/terminal/view/,/webssh/terminal/clissh/view/,/ws/webssh/view/,/ws/clissh/view/,/webguacamole/terminal/view/',NULL,'远程终端',NULL,1,123),(44,'终端会话关闭','/api/webssh/session/close/,/api/webssh/session/rdp/close/,/api/webssh/session/clissh/close/',NULL,'远程终端',NULL,1,123),(45,'终端会话锁定/解锁','/api/webssh/session/lock/,/api/webssh/session/unlock/,/api/webssh/session/clissh/lock/,/api/webssh/session/clissh/unlock/',NULL,'远程终端',NULL,1,123),(46,'webssh终端文件上传','/api/webssh/session/upload/(?P<pk>[0-9]+)/',NULL,'远程终端',NULL,1,123),(47,'webssh终端文件下载','/api/webssh/session/download/(?P<pk>[0-9]+)/',NULL,'远程终端',NULL,1,123),(48,'webguacamole终端文件上传下载','/api/webguacamole/session/upload/',NULL,'远程终端',NULL,1,123),(49,'登陆后su跳转超级用户',NULL,NULL,'远程终端',NULL,1,123),(50,'调度主机','/scheduler/hosts/',NULL,'任务调度','<i class=\"nav-icon fas fa-tasks fa-xs\"></i>',0,17),(51,'调度主机详细','/scheduler/host/(?P<host_id>[0-9]+)/',NULL,'任务调度',NULL,1,123),(52,'调度主机任务','/scheduler/host/(?P<host_id>[0-9]+)/jobs/',NULL,'任务调度',NULL,1,123);
/*!40000 ALTER TABLE `user_permission` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user_user`
--

DROP TABLE IF EXISTS `user_user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `user_user` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `username` varchar(64) NOT NULL,
  `nickname` varchar(64) NOT NULL,
  `password` varchar(256) NOT NULL,
  `email` varchar(254) NOT NULL,
  `sex` varchar(32) NOT NULL,
  `enabled` tinyint(1) NOT NULL,
  `role` smallint(6) NOT NULL,
  `phone` varchar(11) DEFAULT NULL,
  `weixin` varchar(64) DEFAULT NULL,
  `qq` varchar(24) DEFAULT NULL,
  `setting` longtext,
  `memo` longtext,
  `create_time` datetime(6) NOT NULL,
  `last_login_time` datetime(6) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user_user`
--

LOCK TABLES `user_user` WRITE;
/*!40000 ALTER TABLE `user_user` DISABLE KEYS */;
INSERT INTO `user_user` VALUES (1,'admin','超级管理员','eb1d820542977fc977115269254a7788e83e038292c748665b1489a3456f6bd6','admin@admin.com','male',1,1,'','','','{\"clissh\": [{\"name\": \"securecrt\", \"path\": \"C:\\\\Program Files\\\\VanDyke Software\\\\Clients\\\\SecureCRT.exe\", \"args\": \"/T /N \\\"{username}@{host}-{hostname}\\\" /SSH2 /L {login_user} /PASSWORD {login_passwd} {login_host} /P {port}\", \"enable\": true}, {\"name\": \"xshell\", \"path\": \"C:\\\\Program Files (x86)\\\\NetSarang\\\\Xmanager Enterprise 5\\\\Xshell.exe\", \"args\": \"-newtab \\\"{username}@{host}-{hostname}\\\" -url ssh://{login_user}:{login_passwd}@{login_host}:{port}\", \"enable\": false}, {\"name\": \"putty\", \"path\": \"C:\\\\Program Files (x86)\\\\putty\\\\putty.exe\", \"args\": \"-l {login_user} -pw {login_passwd} {login_host} -P {port}\", \"enable\": false}, {\"name\": \"custom\", \"path\": \"\", \"args\": \"\", \"enable\": false}], \"clisftp\": [{\"name\": \"winscp\", \"path\": \"C:\\\\Program Files (x86)\\\\winscp\\\\WinSCP.exe\", \"args\": \"/sessionname=\\\"{username}@{host}-{hostname}\\\" {login_user}:{login_passwd}@{login_host}:{port}\", \"enable\": true}, {\"name\": \"custom\", \"path\": \"\", \"args\": \"\", \"enable\": false}]}','','2021-12-10 14:12:12.144789','2021-12-13 09:45:40.772515');
/*!40000 ALTER TABLE `user_user` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user_user_groups`
--

DROP TABLE IF EXISTS `user_user_groups`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `user_user_groups` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `group_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_user_groups_user_id_group_id_bb60391f_uniq` (`user_id`,`group_id`),
  KEY `user_user_groups_group_id_c57f13c0_fk_user_group_id` (`group_id`),
  CONSTRAINT `user_user_groups_group_id_c57f13c0_fk_user_group_id` FOREIGN KEY (`group_id`) REFERENCES `user_group` (`id`),
  CONSTRAINT `user_user_groups_user_id_13f9a20d_fk_user_user_id` FOREIGN KEY (`user_id`) REFERENCES `user_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user_user_groups`
--

LOCK TABLES `user_user_groups` WRITE;
/*!40000 ALTER TABLE `user_user_groups` DISABLE KEYS */;
/*!40000 ALTER TABLE `user_user_groups` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user_user_permission`
--

DROP TABLE IF EXISTS `user_user_permission`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `user_user_permission` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `permission_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_user_permission_user_id_permission_id_4d081559_uniq` (`user_id`,`permission_id`),
  KEY `user_user_permission_permission_id_72e131d1_fk_user_perm` (`permission_id`),
  CONSTRAINT `user_user_permission_permission_id_72e131d1_fk_user_perm` FOREIGN KEY (`permission_id`) REFERENCES `user_permission` (`id`),
  CONSTRAINT `user_user_permission_user_id_469a61d2_fk_user_user_id` FOREIGN KEY (`user_id`) REFERENCES `user_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user_user_permission`
--

LOCK TABLES `user_user_permission` WRITE;
/*!40000 ALTER TABLE `user_user_permission` DISABLE KEYS */;
/*!40000 ALTER TABLE `user_user_permission` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user_user_remote_user_bind_hosts`
--

DROP TABLE IF EXISTS `user_user_remote_user_bind_hosts`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `user_user_remote_user_bind_hosts` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `remoteuserbindhost_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_user_remote_user_bi_user_id_remoteuserbindho_7bf765ff_uniq` (`user_id`,`remoteuserbindhost_id`),
  KEY `user_user_remote_use_remoteuserbindhost_i_bab8b236_fk_server_re` (`remoteuserbindhost_id`),
  CONSTRAINT `user_user_remote_use_remoteuserbindhost_i_bab8b236_fk_server_re` FOREIGN KEY (`remoteuserbindhost_id`) REFERENCES `server_remoteuserbindhost` (`id`),
  CONSTRAINT `user_user_remote_use_user_id_cc19c3ec_fk_user_user` FOREIGN KEY (`user_id`) REFERENCES `user_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user_user_remote_user_bind_hosts`
--

LOCK TABLES `user_user_remote_user_bind_hosts` WRITE;
/*!40000 ALTER TABLE `user_user_remote_user_bind_hosts` DISABLE KEYS */;
/*!40000 ALTER TABLE `user_user_remote_user_bind_hosts` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `webssh_terminallog`
--

DROP TABLE IF EXISTS `webssh_terminallog`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `webssh_terminallog` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user` varchar(64) NOT NULL,
  `hostname` varchar(128) NOT NULL,
  `ip` char(39) NOT NULL,
  `protocol` varchar(64) NOT NULL,
  `port` smallint(6) NOT NULL,
  `username` varchar(128) NOT NULL,
  `cmd` longtext,
  `detail` varchar(128) DEFAULT NULL,
  `address` char(39) DEFAULT NULL,
  `useragent` varchar(512) DEFAULT NULL,
  `start_time` datetime(6) NOT NULL,
  `create_time` datetime(6) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `webssh_terminallog`
--

LOCK TABLES `webssh_terminallog` WRITE;
/*!40000 ALTER TABLE `webssh_terminallog` DISABLE KEYS */;
/*!40000 ALTER TABLE `webssh_terminallog` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `webssh_terminalsession`
--

DROP TABLE IF EXISTS `webssh_terminalsession`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `webssh_terminalsession` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(512) NOT NULL,
  `group` varchar(512) NOT NULL,
  `type` smallint(6) NOT NULL,
  `user` varchar(128) NOT NULL,
  `host` char(39) NOT NULL,
  `port` smallint(6) NOT NULL,
  `username` varchar(128) NOT NULL,
  `protocol` smallint(6) NOT NULL,
  `address` char(39) DEFAULT NULL,
  `useragent` varchar(512) DEFAULT NULL,
  `locked` tinyint(1) NOT NULL,
  `create_time` datetime(6) NOT NULL,
  `connect_info` varchar(128) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `webssh_terminalsession`
--

LOCK TABLES `webssh_terminalsession` WRITE;
/*!40000 ALTER TABLE `webssh_terminalsession` DISABLE KEYS */;
/*!40000 ALTER TABLE `webssh_terminalsession` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2021-12-13  2:29:44
