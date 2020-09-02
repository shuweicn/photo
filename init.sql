

CREATE DATABASE `photo` /*!40100 DEFAULT CHARACTER SET utf8mb4 */;

USE `photo`;


CREATE TABLE `photo` (
  `id` int NOT NULL AUTO_INCREMENT,
  `src` varchar(200) DEFAULT NULL,
  `pre_src` varchar(200) DEFAULT NULL,
  `pre_dst` varchar(200) DEFAULT NULL,
  `dst` varchar(200) DEFAULT NULL,
  `photo_aae_pair` varchar(200) DEFAULT NULL,
  `aae_final_follow` varchar(200) DEFAULT NULL,
  `photo_duplicate_with` varchar(200) DEFAULT NULL,
  `mtime` datetime DEFAULT NULL,
  `ctime` datetime DEFAULT NULL,
  `md5` varchar(16) DEFAULT NULL,
  `sha256` varchar(64) DEFAULT NULL,
  `exif` json DEFAULT NULL,
  `exif_status` tinyint(1) DEFAULT NULL,
  `exif_type` varchar(10) DEFAULT NULL,
  `file_suffix` varchar(200) DEFAULT NULL,
  `status` varchar(20) DEFAULT NULL,
  `is_moved` tinyint(1) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_photo_src` (`src`),
  KEY `ix_photo_pre_src` (`pre_src`),
  KEY `ix_photo_pre_dst` (`pre_dst`),
  KEY `ix_photo_dst` (`dst`),
  KEY `ix_photo_aae_pair` (`photo_aae_pair`),
  KEY `ix_photo_md5` (`md5`),
  KEY `ix_photo_status` (`status`),
  CONSTRAINT `photo_chk_1` CHECK ((`exif_status` in (0,1))),
  CONSTRAINT `photo_chk_2` CHECK ((`is_moved` in (0,1)))
) ENGINE=MyISAM2  DEFAULT CHARSET=utf8mb4;

