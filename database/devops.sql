/*
Navicat MySQL Data Transfer

Source Server         : 192.168.223.111_devops
Source Server Version : 50727
Source Host           : 192.168.223.111:3306
Source Database       : devops

Target Server Type    : MYSQL
Target Server Version : 50727
File Encoding         : 65001

Date: 2020-04-30 10:23:29
*/

SET FOREIGN_KEY_CHECKS=0;

-- ----------------------------
-- Table structure for auth_group
-- ----------------------------
DROP TABLE IF EXISTS `auth_group`;
CREATE TABLE `auth_group` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(150) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of auth_group
-- ----------------------------

-- ----------------------------
-- Table structure for auth_group_permissions
-- ----------------------------
DROP TABLE IF EXISTS `auth_group_permissions`;
CREATE TABLE `auth_group_permissions` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `group_id` int(11) NOT NULL,
  `permission_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_group_permissions_group_id_permission_id_0cd325b0_uniq` (`group_id`,`permission_id`),
  KEY `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` (`permission_id`),
  CONSTRAINT `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `auth_group_permissions_group_id_b120cbf9_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of auth_group_permissions
-- ----------------------------

-- ----------------------------
-- Table structure for auth_permission
-- ----------------------------
DROP TABLE IF EXISTS `auth_permission`;
CREATE TABLE `auth_permission` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `content_type_id` int(11) NOT NULL,
  `codename` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_permission_content_type_id_codename_01ab375a_uniq` (`content_type_id`,`codename`),
  CONSTRAINT `auth_permission_content_type_id_2f476e4b_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=69 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of auth_permission
-- ----------------------------
INSERT INTO `auth_permission` VALUES ('1', 'Can add permission', '1', 'add_permission');
INSERT INTO `auth_permission` VALUES ('2', 'Can change permission', '1', 'change_permission');
INSERT INTO `auth_permission` VALUES ('3', 'Can delete permission', '1', 'delete_permission');
INSERT INTO `auth_permission` VALUES ('4', 'Can view permission', '1', 'view_permission');
INSERT INTO `auth_permission` VALUES ('5', 'Can add group', '2', 'add_group');
INSERT INTO `auth_permission` VALUES ('6', 'Can change group', '2', 'change_group');
INSERT INTO `auth_permission` VALUES ('7', 'Can delete group', '2', 'delete_group');
INSERT INTO `auth_permission` VALUES ('8', 'Can view group', '2', 'view_group');
INSERT INTO `auth_permission` VALUES ('9', 'Can add user', '3', 'add_user');
INSERT INTO `auth_permission` VALUES ('10', 'Can change user', '3', 'change_user');
INSERT INTO `auth_permission` VALUES ('11', 'Can delete user', '3', 'delete_user');
INSERT INTO `auth_permission` VALUES ('12', 'Can view user', '3', 'view_user');
INSERT INTO `auth_permission` VALUES ('13', 'Can add content type', '4', 'add_contenttype');
INSERT INTO `auth_permission` VALUES ('14', 'Can change content type', '4', 'change_contenttype');
INSERT INTO `auth_permission` VALUES ('15', 'Can delete content type', '4', 'delete_contenttype');
INSERT INTO `auth_permission` VALUES ('16', 'Can view content type', '4', 'view_contenttype');
INSERT INTO `auth_permission` VALUES ('17', 'Can add session', '5', 'add_session');
INSERT INTO `auth_permission` VALUES ('18', 'Can change session', '5', 'change_session');
INSERT INTO `auth_permission` VALUES ('19', 'Can delete session', '5', 'delete_session');
INSERT INTO `auth_permission` VALUES ('20', 'Can view session', '5', 'view_session');
INSERT INTO `auth_permission` VALUES ('21', 'Can add 主机组', '6', 'add_hostgroup');
INSERT INTO `auth_permission` VALUES ('22', 'Can change 主机组', '6', 'change_hostgroup');
INSERT INTO `auth_permission` VALUES ('23', 'Can delete 主机组', '6', 'delete_hostgroup');
INSERT INTO `auth_permission` VALUES ('24', 'Can view 主机组', '6', 'view_hostgroup');
INSERT INTO `auth_permission` VALUES ('25', 'Can add 主机账户', '7', 'add_remoteuser');
INSERT INTO `auth_permission` VALUES ('26', 'Can change 主机账户', '7', 'change_remoteuser');
INSERT INTO `auth_permission` VALUES ('27', 'Can delete 主机账户', '7', 'delete_remoteuser');
INSERT INTO `auth_permission` VALUES ('28', 'Can view 主机账户', '7', 'view_remoteuser');
INSERT INTO `auth_permission` VALUES ('29', 'Can add 远程主机', '8', 'add_remoteuserbindhost');
INSERT INTO `auth_permission` VALUES ('30', 'Can change 远程主机', '8', 'change_remoteuserbindhost');
INSERT INTO `auth_permission` VALUES ('31', 'Can delete 远程主机', '8', 'delete_remoteuserbindhost');
INSERT INTO `auth_permission` VALUES ('32', 'Can view 远程主机', '8', 'view_remoteuserbindhost');
INSERT INTO `auth_permission` VALUES ('33', 'Can add 主机详细', '9', 'add_serverdetail');
INSERT INTO `auth_permission` VALUES ('34', 'Can change 主机详细', '9', 'change_serverdetail');
INSERT INTO `auth_permission` VALUES ('35', 'Can delete 主机详细', '9', 'delete_serverdetail');
INSERT INTO `auth_permission` VALUES ('36', 'Can view 主机详细', '9', 'view_serverdetail');
INSERT INTO `auth_permission` VALUES ('37', 'Can add 用户组', '10', 'add_group');
INSERT INTO `auth_permission` VALUES ('38', 'Can change 用户组', '10', 'change_group');
INSERT INTO `auth_permission` VALUES ('39', 'Can delete 用户组', '10', 'delete_group');
INSERT INTO `auth_permission` VALUES ('40', 'Can view 用户组', '10', 'view_group');
INSERT INTO `auth_permission` VALUES ('41', 'Can add 用户日志', '11', 'add_loginlog');
INSERT INTO `auth_permission` VALUES ('42', 'Can change 用户日志', '11', 'change_loginlog');
INSERT INTO `auth_permission` VALUES ('43', 'Can delete 用户日志', '11', 'delete_loginlog');
INSERT INTO `auth_permission` VALUES ('44', 'Can view 用户日志', '11', 'view_loginlog');
INSERT INTO `auth_permission` VALUES ('45', 'Can add 权限', '12', 'add_permission');
INSERT INTO `auth_permission` VALUES ('46', 'Can change 权限', '12', 'change_permission');
INSERT INTO `auth_permission` VALUES ('47', 'Can delete 权限', '12', 'delete_permission');
INSERT INTO `auth_permission` VALUES ('48', 'Can view 权限', '12', 'view_permission');
INSERT INTO `auth_permission` VALUES ('49', 'Can add 用户', '13', 'add_user');
INSERT INTO `auth_permission` VALUES ('50', 'Can change 用户', '13', 'change_user');
INSERT INTO `auth_permission` VALUES ('51', 'Can delete 用户', '13', 'delete_user');
INSERT INTO `auth_permission` VALUES ('52', 'Can view 用户', '13', 'view_user');
INSERT INTO `auth_permission` VALUES ('53', 'Can add 在线会话日志', '14', 'add_terminallog');
INSERT INTO `auth_permission` VALUES ('54', 'Can change 在线会话日志', '14', 'change_terminallog');
INSERT INTO `auth_permission` VALUES ('55', 'Can delete 在线会话日志', '14', 'delete_terminallog');
INSERT INTO `auth_permission` VALUES ('56', 'Can view 在线会话日志', '14', 'view_terminallog');
INSERT INTO `auth_permission` VALUES ('57', 'Can add 在线会话', '15', 'add_terminalsession');
INSERT INTO `auth_permission` VALUES ('58', 'Can change 在线会话', '15', 'change_terminalsession');
INSERT INTO `auth_permission` VALUES ('59', 'Can delete 在线会话', '15', 'delete_terminalsession');
INSERT INTO `auth_permission` VALUES ('60', 'Can view 在线会话', '15', 'view_terminalsession');
INSERT INTO `auth_permission` VALUES ('61', 'Can add 批量日志', '16', 'add_batchcmdlog');
INSERT INTO `auth_permission` VALUES ('62', 'Can change 批量日志', '16', 'change_batchcmdlog');
INSERT INTO `auth_permission` VALUES ('63', 'Can delete 批量日志', '16', 'delete_batchcmdlog');
INSERT INTO `auth_permission` VALUES ('64', 'Can view 批量日志', '16', 'view_batchcmdlog');
INSERT INTO `auth_permission` VALUES ('65', 'Can add 调度主机', '17', 'add_schedulerhost');
INSERT INTO `auth_permission` VALUES ('66', 'Can change 调度主机', '17', 'change_schedulerhost');
INSERT INTO `auth_permission` VALUES ('67', 'Can delete 调度主机', '17', 'delete_schedulerhost');
INSERT INTO `auth_permission` VALUES ('68', 'Can view 调度主机', '17', 'view_schedulerhost');

-- ----------------------------
-- Table structure for auth_user
-- ----------------------------
DROP TABLE IF EXISTS `auth_user`;
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of auth_user
-- ----------------------------

-- ----------------------------
-- Table structure for auth_user_groups
-- ----------------------------
DROP TABLE IF EXISTS `auth_user_groups`;
CREATE TABLE `auth_user_groups` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `group_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_user_groups_user_id_group_id_94350c0c_uniq` (`user_id`,`group_id`),
  KEY `auth_user_groups_group_id_97559544_fk_auth_group_id` (`group_id`),
  CONSTRAINT `auth_user_groups_group_id_97559544_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`),
  CONSTRAINT `auth_user_groups_user_id_6a12ed8b_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of auth_user_groups
-- ----------------------------

-- ----------------------------
-- Table structure for auth_user_user_permissions
-- ----------------------------
DROP TABLE IF EXISTS `auth_user_user_permissions`;
CREATE TABLE `auth_user_user_permissions` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `permission_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_user_user_permissions_user_id_permission_id_14a6b632_uniq` (`user_id`,`permission_id`),
  KEY `auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm` (`permission_id`),
  CONSTRAINT `auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `auth_user_user_permissions_user_id_a95ead1b_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of auth_user_user_permissions
-- ----------------------------

-- ----------------------------
-- Table structure for batch_batchcmdlog
-- ----------------------------
DROP TABLE IF EXISTS `batch_batchcmdlog`;
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of batch_batchcmdlog
-- ----------------------------

-- ----------------------------
-- Table structure for django_content_type
-- ----------------------------
DROP TABLE IF EXISTS `django_content_type`;
CREATE TABLE `django_content_type` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `app_label` varchar(100) NOT NULL,
  `model` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `django_content_type_app_label_model_76bd3d3b_uniq` (`app_label`,`model`)
) ENGINE=InnoDB AUTO_INCREMENT=18 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of django_content_type
-- ----------------------------
INSERT INTO `django_content_type` VALUES ('2', 'auth', 'group');
INSERT INTO `django_content_type` VALUES ('1', 'auth', 'permission');
INSERT INTO `django_content_type` VALUES ('3', 'auth', 'user');
INSERT INTO `django_content_type` VALUES ('16', 'batch', 'batchcmdlog');
INSERT INTO `django_content_type` VALUES ('4', 'contenttypes', 'contenttype');
INSERT INTO `django_content_type` VALUES ('17', 'scheduler', 'schedulerhost');
INSERT INTO `django_content_type` VALUES ('6', 'server', 'hostgroup');
INSERT INTO `django_content_type` VALUES ('7', 'server', 'remoteuser');
INSERT INTO `django_content_type` VALUES ('8', 'server', 'remoteuserbindhost');
INSERT INTO `django_content_type` VALUES ('9', 'server', 'serverdetail');
INSERT INTO `django_content_type` VALUES ('5', 'sessions', 'session');
INSERT INTO `django_content_type` VALUES ('10', 'user', 'group');
INSERT INTO `django_content_type` VALUES ('11', 'user', 'loginlog');
INSERT INTO `django_content_type` VALUES ('12', 'user', 'permission');
INSERT INTO `django_content_type` VALUES ('13', 'user', 'user');
INSERT INTO `django_content_type` VALUES ('14', 'webssh', 'terminallog');
INSERT INTO `django_content_type` VALUES ('15', 'webssh', 'terminalsession');

-- ----------------------------
-- Table structure for django_migrations
-- ----------------------------
DROP TABLE IF EXISTS `django_migrations`;
CREATE TABLE `django_migrations` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `app` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `applied` datetime(6) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=21 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of django_migrations
-- ----------------------------
INSERT INTO `django_migrations` VALUES ('1', 'contenttypes', '0001_initial', '2019-12-04 16:28:11.882857');
INSERT INTO `django_migrations` VALUES ('2', 'contenttypes', '0002_remove_content_type_name', '2019-12-04 16:28:11.930598');
INSERT INTO `django_migrations` VALUES ('3', 'auth', '0001_initial', '2019-12-04 16:28:11.989992');
INSERT INTO `django_migrations` VALUES ('4', 'auth', '0002_alter_permission_name_max_length', '2019-12-04 16:28:12.372851');
INSERT INTO `django_migrations` VALUES ('5', 'auth', '0003_alter_user_email_max_length', '2019-12-04 16:28:12.405731');
INSERT INTO `django_migrations` VALUES ('6', 'auth', '0004_alter_user_username_opts', '2019-12-04 16:28:12.412078');
INSERT INTO `django_migrations` VALUES ('7', 'auth', '0005_alter_user_last_login_null', '2019-12-04 16:28:12.428573');
INSERT INTO `django_migrations` VALUES ('8', 'auth', '0006_require_contenttypes_0002', '2019-12-04 16:28:12.430315');
INSERT INTO `django_migrations` VALUES ('9', 'auth', '0007_alter_validators_add_error_messages', '2019-12-04 16:28:12.436809');
INSERT INTO `django_migrations` VALUES ('10', 'auth', '0008_alter_user_username_max_length', '2019-12-04 16:28:12.456286');
INSERT INTO `django_migrations` VALUES ('11', 'auth', '0009_alter_user_last_name_max_length', '2019-12-04 16:28:12.480448');
INSERT INTO `django_migrations` VALUES ('12', 'auth', '0010_alter_group_name_max_length', '2019-12-04 16:28:12.501199');
INSERT INTO `django_migrations` VALUES ('13', 'auth', '0011_update_proxy_permissions', '2019-12-04 16:28:12.508316');
INSERT INTO `django_migrations` VALUES ('14', 'batch', '0001_initial', '2019-12-04 16:28:12.542840');
INSERT INTO `django_migrations` VALUES ('15', 'scheduler', '0001_initial', '2019-12-04 16:28:12.651162');
INSERT INTO `django_migrations` VALUES ('16', 'server', '0001_initial', '2019-12-04 16:28:12.871620');
INSERT INTO `django_migrations` VALUES ('17', 'user', '0001_initial', '2019-12-04 16:28:13.112958');
INSERT INTO `django_migrations` VALUES ('18', 'server', '0002_auto_20191204_1626', '2019-12-04 16:28:13.378554');
INSERT INTO `django_migrations` VALUES ('19', 'sessions', '0001_initial', '2019-12-04 16:28:13.407917');
INSERT INTO `django_migrations` VALUES ('20', 'webssh', '0001_initial', '2019-12-04 16:28:13.452044');

-- ----------------------------
-- Table structure for django_session
-- ----------------------------
DROP TABLE IF EXISTS `django_session`;
CREATE TABLE `django_session` (
  `session_key` varchar(40) NOT NULL,
  `session_data` longtext NOT NULL,
  `expire_date` datetime(6) NOT NULL,
  PRIMARY KEY (`session_key`),
  KEY `django_session_expire_date_a5c62663` (`expire_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of django_session
-- ----------------------------

-- ----------------------------
-- Table structure for scheduler_schedulerhost
-- ----------------------------
DROP TABLE IF EXISTS `scheduler_schedulerhost`;
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of scheduler_schedulerhost
-- ----------------------------

-- ----------------------------
-- Table structure for server_hostgroup
-- ----------------------------
DROP TABLE IF EXISTS `server_hostgroup`;
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of server_hostgroup
-- ----------------------------

-- ----------------------------
-- Table structure for server_remoteuser
-- ----------------------------
DROP TABLE IF EXISTS `server_remoteuser`;
CREATE TABLE `server_remoteuser` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(128) NOT NULL,
  `username` varchar(128) NOT NULL,
  `password` varchar(512) NOT NULL,
  `enabled` tinyint(1) NOT NULL,
  `superusername` varchar(128) DEFAULT NULL,
  `superpassword` varchar(512) DEFAULT NULL,
  `memo` longtext,
  `create_time` datetime(6) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of server_remoteuser
-- ----------------------------
INSERT INTO `server_remoteuser` VALUES ('1', '通用root账号', 'root', 'gAAAAABd525Kbiej5kjOR6xR1G8_mApmwuG31gf9kDEo1TgnLSflefuplygqxl_2ht-o82QwCdYacA44RftjCDwih0zw0s4ysA==', '0', null, null, null, '2019-12-04 16:28:58.182768');

-- ----------------------------
-- Table structure for server_remoteuserbindhost
-- ----------------------------
DROP TABLE IF EXISTS `server_remoteuserbindhost`;
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
  `memo` longtext,
  `enabled` tinyint(1) NOT NULL,
  `create_time` datetime(6) NOT NULL,
  `remote_user_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `hostname` (`hostname`),
  UNIQUE KEY `server_remoteuserbindhos_ip_protocol_port_remote__43a07529_uniq` (`ip`,`protocol`,`port`,`remote_user_id`),
  KEY `server_remoteuserbin_remote_user_id_99ea1334_fk_server_re` (`remote_user_id`),
  CONSTRAINT `server_remoteuserbin_remote_user_id_99ea1334_fk_server_re` FOREIGN KEY (`remote_user_id`) REFERENCES `server_remoteuser` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of server_remoteuserbindhost
-- ----------------------------
INSERT INTO `server_remoteuserbindhost` VALUES ('1', 'k8s1', '6', '192.168.223.111', null, '1', '2', '22', 'CentOS 7', '1', null, '1', '2019-12-04 16:28:58.186348', '1');
INSERT INTO `server_remoteuserbindhost` VALUES ('2', 'k8s2', '6', '192.168.223.112', null, '1', '2', '22', 'CentOS 7', '1', '', '0', '2019-12-04 16:28:58.188175', '1');
INSERT INTO `server_remoteuserbindhost` VALUES ('10', 'k8s1_telnet', '1', '192.168.223.111', null, '2', '2', '23', 'centos 7.5', '1', '', '1', '2020-03-26 12:51:43.850887', '1');

-- ----------------------------
-- Table structure for server_remoteuserbindhost_host_group
-- ----------------------------
DROP TABLE IF EXISTS `server_remoteuserbindhost_host_group`;
CREATE TABLE `server_remoteuserbindhost_host_group` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `remoteuserbindhost_id` int(11) NOT NULL,
  `hostgroup_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `server_remoteuserbindhos_remoteuserbindhost_id_ho_e2fa1d83_uniq` (`remoteuserbindhost_id`,`hostgroup_id`),
  KEY `server_remoteuserbin_hostgroup_id_c72cf47f_fk_server_ho` (`hostgroup_id`),
  CONSTRAINT `server_remoteuserbin_hostgroup_id_c72cf47f_fk_server_ho` FOREIGN KEY (`hostgroup_id`) REFERENCES `server_hostgroup` (`id`),
  CONSTRAINT `server_remoteuserbin_remoteuserbindhost_i_45428e4e_fk_server_re` FOREIGN KEY (`remoteuserbindhost_id`) REFERENCES `server_remoteuserbindhost` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of server_remoteuserbindhost_host_group
-- ----------------------------

-- ----------------------------
-- Table structure for server_serverdetail
-- ----------------------------
DROP TABLE IF EXISTS `server_serverdetail`;
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
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of server_serverdetail
-- ----------------------------
INSERT INTO `server_serverdetail` VALUES ('1', 'Intel(R) Core(TM) i7-4790 CPU @ 3.60GHz', '1', '1', '40.0', '8', '0', '3.10.0-862.el7.x86_64', 'CentOS 7.5 x86_64', '[{\"mount\": \"/boot\", \"size_total\": 1063256064, \"size_available\": 925028352, \"fstype\": \"xfs\"}, {\"mount\": \"/\", \"size_total\": 39700664320, \"size_available\": 35133009920, \"fstype\": \"xfs\"}]', '[{\"network_card_name\": \"lo\", \"network_card_mac\": null, \"network_card_ipv4\": {\"broadcast\": \"host\", \"netmask\": \"255.0.0.0\", \"network\": \"127.0.0.0\", \"address\": \"127.0.0.1\"}, \"network_card_ipv4_secondaries\": \"unknown\", \"network_card_ipv6\": [{\"scope\": \"host\", \"prefix\": \"128\", \"address\": \"::1\"}], \"network_card_model\": \"loopback\", \"network_card_mtu\": 65536, \"network_card_status\": true, \"network_card_speed\": null}, {\"network_card_name\": \"ens33\", \"network_card_mac\": \"00:0c:29:dd:b3:c8\", \"network_card_ipv4\": {\"broadcast\": \"192.168.223.255\", \"netmask\": \"255.255.255.0\", \"network\": \"192.168.223.0\", \"address\": \"192.168.223.112\"}, \"network_card_ipv4_secondaries\": \"unknown\", \"network_card_ipv6\": [{\"scope\": \"link\", \"prefix\": \"64\", \"address\": \"fe80::25c3:faac:4a7c:c609\"}], \"network_card_model\": \"ether\", \"network_card_mtu\": 1500, \"network_card_status\": true, \"network_card_speed\": 1000}]', 'VMware Virtual Platform', '2');
INSERT INTO `server_serverdetail` VALUES ('2', 'Intel(R) Core(TM) i7-4790 CPU @ 3.60GHz', '1', '2', '40.0', '8', '2', '3.10.0-862.el7.x86_64', 'CentOS 7.5 x86_64', '[{\"mount\": \"/boot\", \"size_total\": 1063256064, \"size_available\": 925028352, \"fstype\": \"xfs\"}, {\"mount\": \"/\", \"size_total\": 39700664320, \"size_available\": 15304671232, \"fstype\": \"xfs\"}, {\"mount\": \"/var/lib/docker/overlay2\", \"size_total\": 39700664320, \"size_available\": 15304671232, \"fstype\": \"xfs\"}, {\"mount\": \"/var/lib/docker/containers\", \"size_total\": 39700664320, \"size_available\": 15304671232, \"fstype\": \"xfs\"}]', '[{\"network_card_name\": \"lo\", \"network_card_mac\": null, \"network_card_ipv4\": {\"broadcast\": \"host\", \"netmask\": \"255.0.0.0\", \"network\": \"127.0.0.0\", \"address\": \"127.0.0.1\"}, \"network_card_ipv4_secondaries\": \"unknown\", \"network_card_ipv6\": [{\"scope\": \"host\", \"prefix\": \"128\", \"address\": \"::1\"}], \"network_card_model\": \"loopback\", \"network_card_mtu\": 65536, \"network_card_status\": true, \"network_card_speed\": null}, {\"network_card_name\": \"ens33\", \"network_card_mac\": \"00:0c:29:e8:f5:c8\", \"network_card_ipv4\": {\"broadcast\": \"192.168.223.255\", \"netmask\": \"255.255.255.0\", \"network\": \"192.168.223.0\", \"address\": \"192.168.223.111\"}, \"network_card_ipv4_secondaries\": \"unknown\", \"network_card_ipv6\": [{\"scope\": \"link\", \"prefix\": \"64\", \"address\": \"fe80::4a6e:c9fb:4e92:16d9\"}], \"network_card_model\": \"ether\", \"network_card_mtu\": 1500, \"network_card_status\": true, \"network_card_speed\": 1000}]', 'VMware Virtual Platform', '1');

-- ----------------------------
-- Table structure for user_group
-- ----------------------------
DROP TABLE IF EXISTS `user_group`;
CREATE TABLE `user_group` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `group_name` varchar(128) NOT NULL,
  `memo` longtext,
  `create_time` datetime(6) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `group_name` (`group_name`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of user_group
-- ----------------------------
INSERT INTO `user_group` VALUES ('1', '运维', '', '2020-04-13 10:31:26.760161');

-- ----------------------------
-- Table structure for user_group_permission
-- ----------------------------
DROP TABLE IF EXISTS `user_group_permission`;
CREATE TABLE `user_group_permission` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `group_id` int(11) NOT NULL,
  `permission_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_group_permission_group_id_permission_id_a98dbad2_uniq` (`group_id`,`permission_id`),
  KEY `user_group_permissio_permission_id_18e9ae70_fk_user_perm` (`permission_id`),
  CONSTRAINT `user_group_permissio_permission_id_18e9ae70_fk_user_perm` FOREIGN KEY (`permission_id`) REFERENCES `user_permission` (`id`),
  CONSTRAINT `user_group_permission_group_id_c223ed5c_fk_user_group_id` FOREIGN KEY (`group_id`) REFERENCES `user_group` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of user_group_permission
-- ----------------------------

-- ----------------------------
-- Table structure for user_group_remote_user_bind_hosts
-- ----------------------------
DROP TABLE IF EXISTS `user_group_remote_user_bind_hosts`;
CREATE TABLE `user_group_remote_user_bind_hosts` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `group_id` int(11) NOT NULL,
  `remoteuserbindhost_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_group_remote_user_b_group_id_remoteuserbindh_5f9f2469_uniq` (`group_id`,`remoteuserbindhost_id`),
  KEY `user_group_remote_us_remoteuserbindhost_i_4252c8c9_fk_server_re` (`remoteuserbindhost_id`),
  CONSTRAINT `user_group_remote_us_group_id_8bf7ba65_fk_user_grou` FOREIGN KEY (`group_id`) REFERENCES `user_group` (`id`),
  CONSTRAINT `user_group_remote_us_remoteuserbindhost_i_4252c8c9_fk_server_re` FOREIGN KEY (`remoteuserbindhost_id`) REFERENCES `server_remoteuserbindhost` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of user_group_remote_user_bind_hosts
-- ----------------------------
INSERT INTO `user_group_remote_user_bind_hosts` VALUES ('4', '1', '1');
INSERT INTO `user_group_remote_user_bind_hosts` VALUES ('3', '1', '2');
INSERT INTO `user_group_remote_user_bind_hosts` VALUES ('2', '1', '10');

-- ----------------------------
-- Table structure for user_loginlog
-- ----------------------------
DROP TABLE IF EXISTS `user_loginlog`;
CREATE TABLE `user_loginlog` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user` varchar(64) DEFAULT NULL,
  `event_type` smallint(6) NOT NULL,
  `detail` longtext NOT NULL,
  `address` char(39) DEFAULT NULL,
  `useragent` varchar(512) DEFAULT NULL,
  `create_time` datetime(6) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of user_loginlog
-- ----------------------------

-- ----------------------------
-- Table structure for user_permission
-- ----------------------------
DROP TABLE IF EXISTS `user_permission`;
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
) ENGINE=InnoDB AUTO_INCREMENT=53 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of user_permission
-- ----------------------------
INSERT INTO `user_permission` VALUES ('1', '仪表盘', '/server/', '<i class=\"nav-icon fas fa-tachometer-alt fa-xs\"></i>', null, null, '0', '1');
INSERT INTO `user_permission` VALUES ('2', '用户', '/user/users/', null, '用户管理', '<i class=\"nav-icon fas fa-user fa-xs\"></i>', '0', '2');
INSERT INTO `user_permission` VALUES ('3', '组', '/user/groups/', null, '用户管理', '<i class=\"nav-icon fas fa-user fa-xs\"></i>', '0', '3');
INSERT INTO `user_permission` VALUES ('4', '主机', '/server/hosts/', null, '主机管理', '<i class=\"nav-icon fas fa-copy fa-xs\"></i>', '0', '4');
INSERT INTO `user_permission` VALUES ('5', '主机组', '/server/groups/', null, '主机管理', '<i class=\"nav-icon fas fa-copy fa-xs\"></i>', '0', '5');
INSERT INTO `user_permission` VALUES ('6', '远程用户', '/server/users/', null, '主机管理', '<i class=\"nav-icon fas fa-copy fa-xs\"></i>', '0', '6');
INSERT INTO `user_permission` VALUES ('7', '终端登录', '/webssh/hosts/', null, '远程终端', '<i class=\"nav-icon fas fa-coffee fa-xs\"></i>', '0', '7');
INSERT INTO `user_permission` VALUES ('8', '在线终端', '/webssh/sessions/', null, '远程终端', '<i class=\"nav-icon fas fa-coffee fa-xs\"></i>', '0', '8');
INSERT INTO `user_permission` VALUES ('9', '批量命令', '/batch/cmd/,/api/batch/get/hosts/,/ws/cmd/', null, '批量处理', '<i class=\"nav-icon fas fa-align-justify fa-xs\"></i>', '0', '9');
INSERT INTO `user_permission` VALUES ('10', '批量脚本', '/batch/script/,/api/batch/get/hosts/,/ws/script/', null, '批量处理', '<i class=\"nav-icon fas fa-align-justify fa-xs\"></i>', '0', '10');
INSERT INTO `user_permission` VALUES ('11', '上传文件', '/batch/file/,/api/batch/upload/,/ws/file/', null, '批量处理', '<i class=\"nav-icon fas fa-align-justify fa-xs\"></i>', '0', '11');
INSERT INTO `user_permission` VALUES ('12', 'module', '/batch/module/,/ws/module/', null, '批量处理', '<i class=\"nav-icon fas fa-align-justify fa-xs\"></i>', '0', '12');
INSERT INTO `user_permission` VALUES ('13', 'playbook', '/batch/playbook/,/ws/playbook/', null, '批量处理', '<i class=\"nav-icon fas fa-align-justify fa-xs\"></i>', '0', '13');
INSERT INTO `user_permission` VALUES ('14', '操作日志', '/user/logs/,/api/user/logs/', null, '日志审计', '<i class=\"nav-icon fas fa-history fa-xs\"></i>', '0', '14');
INSERT INTO `user_permission` VALUES ('15', '终端日志', '/webssh/logs/,/api/webssh/logs/', null, '日志审计', '<i class=\"nav-icon fas fa-history fa-xs\"></i>', '0', '15');
INSERT INTO `user_permission` VALUES ('16', '批量日志', '/batch/logs/,/api/batch/logs/', null, '日志审计', '<i class=\"nav-icon fas fa-history fa-xs\"></i>', '0', '16');
INSERT INTO `user_permission` VALUES ('17', '用户详细', '/user/user/(?P<user_id>[0-9]+)/', null, '用户管理', null, '1', '123');
INSERT INTO `user_permission` VALUES ('18', '用户编辑', '/user/user/(?P<user_id>[0-9]+)/edit/,/api/user/user/update/', null, '用户管理', null, '1', '123');
INSERT INTO `user_permission` VALUES ('19', '用户删除', '/api/user/user/delete/', null, '用户管理', null, '1', '123');
INSERT INTO `user_permission` VALUES ('20', '用户添加', '/user/user/add/,/api/user/user/add/', null, '用户管理', null, '1', '123');
INSERT INTO `user_permission` VALUES ('21', '组详细', '/user/group/(?P<group_id>[0-9]+)/', null, '用户管理', null, '1', '123');
INSERT INTO `user_permission` VALUES ('22', '组编辑', '/user/group/(?P<group_id>[0-9]+)/edit/,/api/user/group/update/', null, '用户管理', null, '1', '123');
INSERT INTO `user_permission` VALUES ('23', '组删除', '/api/user/group/delete/', null, '用户管理', null, '1', '123');
INSERT INTO `user_permission` VALUES ('24', '组添加', '/user/group/add/,/api/user/group/add/', null, '用户管理', null, '1', '123');
INSERT INTO `user_permission` VALUES ('25', '主机详细', '/server/host/(?P<host_id>[0-9]+)/', null, '主机管理', null, '1', '123');
INSERT INTO `user_permission` VALUES ('26', '主机编辑', '/server/host/(?P<host_id>[0-9]+)/edit/,/api/server/host/update/', null, '主机管理', null, '1', '123');
INSERT INTO `user_permission` VALUES ('27', '主机删除', '/api/server/host/delete/', null, '主机管理', null, '1', '123');
INSERT INTO `user_permission` VALUES ('28', '主机添加', '/server/host/add/,/api/server/host/add/', null, '主机管理', null, '1', '123');
INSERT INTO `user_permission` VALUES ('29', '主机更新', '/api/server/host/update/info/', null, '主机管理', null, '1', '123');
INSERT INTO `user_permission` VALUES ('30', '主机组详细', '/server/group/(?P<group_id>[0-9]+)/', null, '主机管理', null, '1', '123');
INSERT INTO `user_permission` VALUES ('31', '主机组编辑', '/server/group/(?P<group_id>[0-9]+)/edit/,/api/server/group/update/', null, '主机管理', null, '1', '123');
INSERT INTO `user_permission` VALUES ('32', '主机组删除', '/api/server/group/delete/', null, '主机管理', null, '1', '123');
INSERT INTO `user_permission` VALUES ('33', '主机组添加', '/server/group/add/,/api/server/group/add/', null, '主机管理', null, '1', '123');
INSERT INTO `user_permission` VALUES ('34', '远程用户详细', '/server/user/(?P<user_id>[0-9]+)/', null, '主机管理', null, '1', '123');
INSERT INTO `user_permission` VALUES ('35', '远程用户编辑', '/server/user/(?P<user_id>[0-9]+)/edit/,/api/server/user/update/', null, '主机管理', null, '1', '123');
INSERT INTO `user_permission` VALUES ('36', '远程用户删除', '/api/server/user/delete/', null, '主机管理', null, '1', '123');
INSERT INTO `user_permission` VALUES ('37', '远程用户添加', '/server/user/add/,/api/server/user/add/', null, '主机管理', null, '1', '123');
INSERT INTO `user_permission` VALUES ('38', 'webssh终端', '/webssh/terminal/,/ws/webssh/', null, '远程终端', null, '1', '123');
INSERT INTO `user_permission` VALUES ('39', '客户端ssh', '/webssh/terminal/cli/', null, '远程终端', null, '1', '123');
INSERT INTO `user_permission` VALUES ('40', '客户端sftp', '/webssh/terminal/cli/sftp', null, '远程终端', null, '1', '123');
INSERT INTO `user_permission` VALUES ('41', 'webtelnet终端', '/webtelnet/terminal/,/ws/webtelnet/', null, '远程终端', null, '1', '123');
INSERT INTO `user_permission` VALUES ('42', 'webguacamole终端', '/webguacamole/terminal/,/ws/webguacamole/', null, '远程终端', null, '1', '123');
INSERT INTO `user_permission` VALUES ('43', '终端会话查看', '/webssh/terminal/view/,/webssh/terminal/clissh/view/,/ws/webssh/view/,/ws/clissh/view/,/webguacamole/terminal/view/', null, '远程终端', null, '1', '123');
INSERT INTO `user_permission` VALUES ('44', '终端会话关闭', '/api/webssh/session/close/,/api/webssh/session/rdp/close/,/api/webssh/session/clissh/close/', null, '远程终端', null, '1', '123');
INSERT INTO `user_permission` VALUES ('45', '终端会话锁定/解锁', '/api/webssh/session/lock/,/api/webssh/session/unlock/,/api/webssh/session/clissh/lock/,/api/webssh/session/clissh/unlock/', null, '远程终端', null, '1', '123');
INSERT INTO `user_permission` VALUES ('46', 'webssh终端文件上传', '/api/webssh/session/upload/(?P<pk>[0-9]+)/', null, '远程终端', null, '1', '123');
INSERT INTO `user_permission` VALUES ('47', 'webssh终端文件下载', '/api/webssh/session/download/(?P<pk>[0-9]+)/', null, '远程终端', null, '1', '123');
INSERT INTO `user_permission` VALUES ('48', 'webguacamole终端文件上传下载', '/api/webguacamole/session/upload/', null, '远程终端', null, '1', '123');
INSERT INTO `user_permission` VALUES ('49', '登陆后su跳转超级用户', null, null, '远程终端', null, '1', '123');
INSERT INTO `user_permission` VALUES ('50', '调度主机', '/scheduler/hosts/', null, '任务调度', '<i class=\"nav-icon fas fa-tasks fa-xs\"></i>', '0', '17');
INSERT INTO `user_permission` VALUES ('51', '调度主机详细', '/scheduler/host/(?P<host_id>[0-9]+)/', null, '任务调度', null, '1', '123');
INSERT INTO `user_permission` VALUES ('52', '调度主机任务', '/scheduler/host/(?P<host_id>[0-9]+)/jobs/', null, '任务调度', null, '1', '123');

-- ----------------------------
-- Table structure for user_user
-- ----------------------------
DROP TABLE IF EXISTS `user_user`;
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
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of user_user
-- ----------------------------
INSERT INTO `user_user` VALUES ('1', 'admin', '超级管理员', 'eb1d820542977fc977115269254a7788e83e038292c748665b1489a3456f6bd6', 'admin@admin.com', 'male', '1', '1', '', '', '', '{\"clissh\": [{\"name\": \"securecrt\", \"path\": \"C:\\\\Program Files\\\\VanDyke Software\\\\Clients\\\\SecureCRT.exe\", \"args\": \"/T /N \\\"{username}@{host}-{hostname}\\\" /SSH2 /L {login_user} /PASSWORD {login_passwd} {login_host} /P {port}\", \"enable\": true}, {\"name\": \"xshell\", \"path\": \"C:\\\\Program Files (x86)\\\\NetSarang\\\\Xmanager Enterprise 5\\\\Xshell.exe\", \"args\": \"-newtab \\\"{username}@{host}-{hostname}\\\" -url ssh://{login_user}:{login_passwd}@{login_host}:{port}\", \"enable\": false}, {\"name\": \"putty\", \"path\": \"C:\\\\Users\\\\xx\\\\AppData\\\\Roaming\\\\TP4A\\\\Teleport-Assist\\\\tools\\\\putty\\\\putty.exe\", \"args\": \"-l {login_user} -pw {login_passwd} {login_host} -P {port}\", \"enable\": false}, {\"name\": \"custom\", \"path\": \"\", \"args\": \"\", \"enable\": false}], \"clisftp\": [{\"name\": \"winscp\", \"path\": \"C:\\\\Program Files (x86)\\\\WinSCP\\\\WinSCP.exe\", \"args\": \"/sessionname=\\\"{username}@{host}-{hostname}\\\" {login_user}:{login_passwd}@{login_host}:{port}\", \"enable\": true}, {\"name\": \"custom\", \"path\": \"\", \"args\": \"\", \"enable\": false}]}', '', '2019-12-04 16:28:58.171590', '2020-04-30 10:18:20.906648');
INSERT INTO `user_user` VALUES ('3', 'leffss', 'leffss', 'eb1d820542977fc977115269254a7788e83e038292c748665b1489a3456f6bd6', 'leffss@126.com', 'male', '1', '1', '', '', '', '{\"clissh\": [{\"name\": \"securecrt\", \"path\": \"C:\\\\Program Files\\\\VanDyke Software\\\\Clients\\\\SecureCRT.exe\", \"args\": \"/T /N \\\"{username}@{host}-{hostname}\\\" /SSH2 /L {login_user} /PASSWORD {login_passwd} {login_host} /P {port}\", \"enable\": true}, {\"name\": \"xshell\", \"path\": \"C:\\\\Program Files (x86)\\\\NetSarang\\\\Xmanager Enterprise 5\\\\Xshell.exe\", \"args\": \"-newtab \\\"{username}@{host}-{hostname}\\\" -url ssh://{login_user}:{login_passwd}@{login_host}:{port}\", \"enable\": false}, {\"name\": \"putty\", \"path\": \"C:\\\\Users\\\\xx\\\\AppData\\\\Roaming\\\\TP4A\\\\Teleport-Assist\\\\tools\\\\putty\\\\putty.exe\", \"args\": \"-l {login_user} -pw {login_passwd} {login_host} -P {port}\", \"enable\": false}, {\"name\": \"custom\", \"path\": \"\", \"args\": \"\", \"enable\": false}], \"clisftp\": [{\"name\": \"winscp\", \"path\": \"C:\\\\Program Files\\\\winscp\\\\WinSCP.exe\", \"args\": \"/sessionname=\\\"{username}@{host}-{hostname}\\\" {login_user}:{login_passwd}@{login_host}:{port}\", \"enable\": true}, {\"name\": \"custom\", \"path\": \"\", \"args\": \"\", \"enable\": false}]}', '', '2020-04-13 10:29:59.670448', '2020-04-20 15:24:21.094405');

-- ----------------------------
-- Table structure for user_user_groups
-- ----------------------------
DROP TABLE IF EXISTS `user_user_groups`;
CREATE TABLE `user_user_groups` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `group_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_user_groups_user_id_group_id_bb60391f_uniq` (`user_id`,`group_id`),
  KEY `user_user_groups_group_id_c57f13c0_fk_user_group_id` (`group_id`),
  CONSTRAINT `user_user_groups_group_id_c57f13c0_fk_user_group_id` FOREIGN KEY (`group_id`) REFERENCES `user_group` (`id`),
  CONSTRAINT `user_user_groups_user_id_13f9a20d_fk_user_user_id` FOREIGN KEY (`user_id`) REFERENCES `user_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of user_user_groups
-- ----------------------------
INSERT INTO `user_user_groups` VALUES ('1', '3', '1');

-- ----------------------------
-- Table structure for user_user_permission
-- ----------------------------
DROP TABLE IF EXISTS `user_user_permission`;
CREATE TABLE `user_user_permission` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `permission_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_user_permission_user_id_permission_id_4d081559_uniq` (`user_id`,`permission_id`),
  KEY `user_user_permission_permission_id_72e131d1_fk_user_perm` (`permission_id`),
  CONSTRAINT `user_user_permission_permission_id_72e131d1_fk_user_perm` FOREIGN KEY (`permission_id`) REFERENCES `user_permission` (`id`),
  CONSTRAINT `user_user_permission_user_id_469a61d2_fk_user_user_id` FOREIGN KEY (`user_id`) REFERENCES `user_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=99 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of user_user_permission
-- ----------------------------
INSERT INTO `user_user_permission` VALUES ('52', '3', '1');
INSERT INTO `user_user_permission` VALUES ('53', '3', '2');
INSERT INTO `user_user_permission` VALUES ('54', '3', '3');
INSERT INTO `user_user_permission` VALUES ('55', '3', '4');
INSERT INTO `user_user_permission` VALUES ('56', '3', '5');
INSERT INTO `user_user_permission` VALUES ('57', '3', '6');
INSERT INTO `user_user_permission` VALUES ('58', '3', '7');
INSERT INTO `user_user_permission` VALUES ('59', '3', '8');
INSERT INTO `user_user_permission` VALUES ('60', '3', '9');
INSERT INTO `user_user_permission` VALUES ('61', '3', '10');
INSERT INTO `user_user_permission` VALUES ('62', '3', '11');
INSERT INTO `user_user_permission` VALUES ('63', '3', '12');
INSERT INTO `user_user_permission` VALUES ('64', '3', '13');
INSERT INTO `user_user_permission` VALUES ('65', '3', '14');
INSERT INTO `user_user_permission` VALUES ('66', '3', '15');
INSERT INTO `user_user_permission` VALUES ('67', '3', '16');
INSERT INTO `user_user_permission` VALUES ('68', '3', '17');
INSERT INTO `user_user_permission` VALUES ('69', '3', '18');
INSERT INTO `user_user_permission` VALUES ('70', '3', '19');
INSERT INTO `user_user_permission` VALUES ('71', '3', '20');
INSERT INTO `user_user_permission` VALUES ('72', '3', '21');
INSERT INTO `user_user_permission` VALUES ('73', '3', '22');
INSERT INTO `user_user_permission` VALUES ('74', '3', '23');
INSERT INTO `user_user_permission` VALUES ('75', '3', '24');
INSERT INTO `user_user_permission` VALUES ('76', '3', '25');
INSERT INTO `user_user_permission` VALUES ('77', '3', '26');
INSERT INTO `user_user_permission` VALUES ('78', '3', '27');
INSERT INTO `user_user_permission` VALUES ('79', '3', '28');
INSERT INTO `user_user_permission` VALUES ('80', '3', '29');
INSERT INTO `user_user_permission` VALUES ('81', '3', '30');
INSERT INTO `user_user_permission` VALUES ('82', '3', '31');
INSERT INTO `user_user_permission` VALUES ('83', '3', '32');
INSERT INTO `user_user_permission` VALUES ('84', '3', '33');
INSERT INTO `user_user_permission` VALUES ('85', '3', '34');
INSERT INTO `user_user_permission` VALUES ('86', '3', '35');
INSERT INTO `user_user_permission` VALUES ('87', '3', '36');
INSERT INTO `user_user_permission` VALUES ('88', '3', '37');
INSERT INTO `user_user_permission` VALUES ('89', '3', '38');
INSERT INTO `user_user_permission` VALUES ('90', '3', '39');
INSERT INTO `user_user_permission` VALUES ('91', '3', '40');
INSERT INTO `user_user_permission` VALUES ('92', '3', '41');
INSERT INTO `user_user_permission` VALUES ('93', '3', '42');
INSERT INTO `user_user_permission` VALUES ('94', '3', '43');
INSERT INTO `user_user_permission` VALUES ('95', '3', '44');
INSERT INTO `user_user_permission` VALUES ('96', '3', '45');
INSERT INTO `user_user_permission` VALUES ('97', '3', '46');
INSERT INTO `user_user_permission` VALUES ('98', '3', '47');

-- ----------------------------
-- Table structure for user_user_remote_user_bind_hosts
-- ----------------------------
DROP TABLE IF EXISTS `user_user_remote_user_bind_hosts`;
CREATE TABLE `user_user_remote_user_bind_hosts` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `remoteuserbindhost_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_user_remote_user_bi_user_id_remoteuserbindho_7bf765ff_uniq` (`user_id`,`remoteuserbindhost_id`),
  KEY `user_user_remote_use_remoteuserbindhost_i_bab8b236_fk_server_re` (`remoteuserbindhost_id`),
  CONSTRAINT `user_user_remote_use_remoteuserbindhost_i_bab8b236_fk_server_re` FOREIGN KEY (`remoteuserbindhost_id`) REFERENCES `server_remoteuserbindhost` (`id`),
  CONSTRAINT `user_user_remote_use_user_id_cc19c3ec_fk_user_user` FOREIGN KEY (`user_id`) REFERENCES `user_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of user_user_remote_user_bind_hosts
-- ----------------------------

-- ----------------------------
-- Table structure for webssh_terminallog
-- ----------------------------
DROP TABLE IF EXISTS `webssh_terminallog`;
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of webssh_terminallog
-- ----------------------------

-- ----------------------------
-- Table structure for webssh_terminalsession
-- ----------------------------
DROP TABLE IF EXISTS `webssh_terminalsession`;
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
) ENGINE=InnoDB AUTO_INCREMENT=78 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of webssh_terminalsession
-- ----------------------------
