-- ============================================================
-- 重点人员信息管理系统 - 数据库初始化脚本
-- Database: key_person_mgmt
-- ============================================================

CREATE DATABASE IF NOT EXISTS key_person_mgmt
  DEFAULT CHARACTER SET utf8mb4
  DEFAULT COLLATE utf8mb4_unicode_ci;

USE key_person_mgmt;

SET FOREIGN_KEY_CHECKS = 0;

-- -----------------------------------------------------------
-- 1. 部门/派出所表
-- -----------------------------------------------------------
DROP TABLE IF EXISTS `department`;
CREATE TABLE `department` (
  `dept_id`      INT          NOT NULL AUTO_INCREMENT,
  `dept_name`    VARCHAR(100) NOT NULL COMMENT '部门名称',
  `dept_code`    VARCHAR(50)  NOT NULL COMMENT '部门编码',
  `parent_id`    INT                   DEFAULT NULL COMMENT '上级部门ID',
  `address`      VARCHAR(255)          DEFAULT NULL COMMENT '地址',
  `phone`        VARCHAR(20)           DEFAULT NULL COMMENT '联系电话',
  `status`       TINYINT      NOT NULL DEFAULT 1 COMMENT '状态 1启用 0停用',
  `created_at`   DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at`   DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`dept_id`),
  UNIQUE KEY `uk_dept_code` (`dept_code`),
  KEY `idx_parent_id` (`parent_id`),
  CONSTRAINT `fk_dept_parent` FOREIGN KEY (`parent_id`) REFERENCES `department` (`dept_id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='部门/派出所';

-- -----------------------------------------------------------
-- 2. 系统用户表
-- -----------------------------------------------------------
DROP TABLE IF EXISTS `sys_user`;
CREATE TABLE `sys_user` (
  `user_id`       INT          NOT NULL AUTO_INCREMENT,
  `username`      VARCHAR(50)  NOT NULL COMMENT '登录名',
  `password`      VARCHAR(255) NOT NULL COMMENT '密码(bcrypt)',
  `real_name`     VARCHAR(50)  NOT NULL COMMENT '真实姓名',
  `role`          ENUM('admin','operator') NOT NULL DEFAULT 'operator' COMMENT '角色',
  `department_id` INT                   DEFAULT NULL COMMENT '所属部门ID',
  `phone`         VARCHAR(20)           DEFAULT NULL COMMENT '手机号',
  `status`        TINYINT      NOT NULL DEFAULT 1 COMMENT '状态 1启用 0停用',
  `created_at`    DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at`    DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`user_id`),
  UNIQUE KEY `uk_username` (`username`),
  KEY `idx_department` (`department_id`),
  CONSTRAINT `fk_user_dept` FOREIGN KEY (`department_id`) REFERENCES `department` (`dept_id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='系统用户';

-- -----------------------------------------------------------
-- 3. 人员类别表
-- -----------------------------------------------------------
DROP TABLE IF EXISTS `person_category`;
CREATE TABLE `person_category` (
  `category_id`   INT          NOT NULL AUTO_INCREMENT,
  `category_name` VARCHAR(50)  NOT NULL COMMENT '类别名称',
  `category_code` VARCHAR(50)  NOT NULL COMMENT '类别编码',
  `description`   TEXT                  DEFAULT NULL COMMENT '描述',
  `status`        TINYINT      NOT NULL DEFAULT 1 COMMENT '状态 1启用 0停用',
  `sort_order`    INT          NOT NULL DEFAULT 0 COMMENT '排序',
  `created_at`    DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at`    DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`category_id`),
  UNIQUE KEY `uk_category_code` (`category_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='人员类别';

-- -----------------------------------------------------------
-- 4. 重点人员主表
-- -----------------------------------------------------------
DROP TABLE IF EXISTS `key_person`;
CREATE TABLE `key_person` (
  `person_id`       INT          NOT NULL AUTO_INCREMENT,
  `name`            VARCHAR(50)  NOT NULL COMMENT '姓名',
  `gender`          ENUM('M','F')         DEFAULT NULL COMMENT '性别 M男 F女',
  `id_card`         VARCHAR(18)  NOT NULL COMMENT '身份证号',
  `birth_date`      DATE                  DEFAULT NULL COMMENT '出生日期',
  `phone`           VARCHAR(20)           DEFAULT NULL COMMENT '手机号',
  `address`         VARCHAR(255)          DEFAULT NULL COMMENT '户籍地址',
  `current_address` VARCHAR(255)          DEFAULT NULL COMMENT '现住地址',
  `photo_url`       VARCHAR(255)          DEFAULT NULL COMMENT '照片URL',
  `category_id`     INT                   DEFAULT NULL COMMENT '人员类别',
  `risk_level`      ENUM('high','medium','low') NOT NULL DEFAULT 'medium' COMMENT '风险等级',
  `department_id`   INT                   DEFAULT NULL COMMENT '管辖部门',
  `control_status`  ENUM('monitored','removed','archived') NOT NULL DEFAULT 'monitored' COMMENT '管控状态',
  `case_description` TEXT                 DEFAULT NULL COMMENT '主要事由/案情摘要',
  `created_by`      INT                   DEFAULT NULL COMMENT '创建人',
  `created_at`      DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at`      DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`person_id`),
  UNIQUE KEY `uk_id_card` (`id_card`),
  KEY `idx_category` (`category_id`),
  KEY `idx_department` (`department_id`),
  KEY `idx_risk_level` (`risk_level`),
  KEY `idx_control_status` (`control_status`),
  KEY `idx_created_by` (`created_by`),
  CONSTRAINT `fk_person_category` FOREIGN KEY (`category_id`) REFERENCES `person_category` (`category_id`) ON DELETE SET NULL,
  CONSTRAINT `fk_person_dept` FOREIGN KEY (`department_id`) REFERENCES `department` (`dept_id`) ON DELETE SET NULL,
  CONSTRAINT `fk_person_creator` FOREIGN KEY (`created_by`) REFERENCES `sys_user` (`user_id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='重点人员信息';

-- -----------------------------------------------------------
-- 5. 联系人/家属表
-- -----------------------------------------------------------
DROP TABLE IF EXISTS `person_contact`;
CREATE TABLE `person_contact` (
  `contact_id`   INT          NOT NULL AUTO_INCREMENT,
  `person_id`    INT          NOT NULL COMMENT '关联重点人员ID',
  `name`         VARCHAR(50)  NOT NULL COMMENT '姓名',
  `relation`     VARCHAR(50)           DEFAULT NULL COMMENT '关系(配偶/子女/父母等)',
  `phone`        VARCHAR(20)           DEFAULT NULL COMMENT '联系电话',
  `address`      VARCHAR(255)          DEFAULT NULL COMMENT '住址',
  `is_emergency` TINYINT      NOT NULL DEFAULT 0 COMMENT '是否紧急联系人 0否1是',
  `created_at`   DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at`   DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`contact_id`),
  KEY `idx_person_id` (`person_id`),
  CONSTRAINT `fk_contact_person` FOREIGN KEY (`person_id`) REFERENCES `key_person` (`person_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='人员联系人';

-- -----------------------------------------------------------
-- 6. 涉案信息表
-- -----------------------------------------------------------
DROP TABLE IF EXISTS `person_case`;
CREATE TABLE `person_case` (
  `case_id`     INT          NOT NULL AUTO_INCREMENT,
  `person_id`   INT          NOT NULL COMMENT '关联重点人员ID',
  `case_number` VARCHAR(100)          DEFAULT NULL COMMENT '案件编号',
  `case_name`   VARCHAR(200) NOT NULL COMMENT '案件名称',
  `case_type`   VARCHAR(50)           DEFAULT NULL COMMENT '案件类型',
  `case_date`   DATE                  DEFAULT NULL COMMENT '案发日期',
  `case_status` VARCHAR(50)           DEFAULT NULL COMMENT '案件状态',
  `description` TEXT                  DEFAULT NULL COMMENT '案情描述',
  `created_by`  INT                   DEFAULT NULL COMMENT '记录人',
  `created_at`  DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at`  DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`case_id`),
  KEY `idx_person_id` (`person_id`),
  KEY `idx_created_by` (`created_by`),
  CONSTRAINT `fk_case_person` FOREIGN KEY (`person_id`) REFERENCES `key_person` (`person_id`) ON DELETE CASCADE,
  CONSTRAINT `fk_case_creator` FOREIGN KEY (`created_by`) REFERENCES `sys_user` (`user_id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='涉案信息';

-- -----------------------------------------------------------
-- 7. 活动轨迹表
-- -----------------------------------------------------------
DROP TABLE IF EXISTS `person_track`;
CREATE TABLE `person_track` (
  `track_id`      INT          NOT NULL AUTO_INCREMENT,
  `person_id`     INT          NOT NULL COMMENT '关联重点人员ID',
  `track_time`    DATETIME     NOT NULL COMMENT '活动时间',
  `location`      VARCHAR(255) NOT NULL COMMENT '地点',
  `longitude`     DECIMAL(10,7)         DEFAULT NULL COMMENT '经度',
  `latitude`      DECIMAL(10,7)         DEFAULT NULL COMMENT '纬度',
  `activity_type` VARCHAR(50)           DEFAULT NULL COMMENT '活动类型',
  `description`   TEXT                  DEFAULT NULL COMMENT '活动描述',
  `source`        VARCHAR(100)          DEFAULT NULL COMMENT '信息来源',
  `created_at`    DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`track_id`),
  KEY `idx_person_id` (`person_id`),
  KEY `idx_track_time` (`track_time`),
  CONSTRAINT `fk_track_person` FOREIGN KEY (`person_id`) REFERENCES `key_person` (`person_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='活动轨迹';

-- -----------------------------------------------------------
-- 8. 预警信息表
-- -----------------------------------------------------------
DROP TABLE IF EXISTS `person_alert`;
CREATE TABLE `person_alert` (
  `alert_id`      INT          NOT NULL AUTO_INCREMENT,
  `person_id`     INT          NOT NULL COMMENT '关联重点人员ID',
  `alert_type`    VARCHAR(50)  NOT NULL COMMENT '预警类型',
  `alert_content` TEXT         NOT NULL COMMENT '预警内容',
  `alert_level`   ENUM('urgent','important','normal') NOT NULL DEFAULT 'normal' COMMENT '预警等级',
  `alert_time`    DATETIME     NOT NULL COMMENT '预警时间',
  `handler_id`    INT                   DEFAULT NULL COMMENT '处理人',
  `handle_time`   DATETIME              DEFAULT NULL COMMENT '处理时间',
  `handle_result` TEXT                  DEFAULT NULL COMMENT '处理结果',
  `status`        ENUM('pending','handled','dismissed') NOT NULL DEFAULT 'pending' COMMENT '状态',
  `created_at`    DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at`    DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`alert_id`),
  KEY `idx_person_id` (`person_id`),
  KEY `idx_handler` (`handler_id`),
  KEY `idx_status` (`status`),
  KEY `idx_alert_level` (`alert_level`),
  CONSTRAINT `fk_alert_person` FOREIGN KEY (`person_id`) REFERENCES `key_person` (`person_id`) ON DELETE CASCADE,
  CONSTRAINT `fk_alert_handler` FOREIGN KEY (`handler_id`) REFERENCES `sys_user` (`user_id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='预警信息';

-- ============================================================
-- 初始数据
-- ============================================================

-- 部门
INSERT INTO `department` (`dept_name`, `dept_code`, `parent_id`, `address`, `phone`) VALUES
('市公安局', 'POLICE_HQ', NULL, '市解放路1号', '010-12345678'),
('城关派出所', 'POLICE_CG', 1, '城关街道中心路10号', '010-12345601'),
('河西派出所', 'POLICE_HX', 1, '河西街道建设路20号', '010-12345602');

-- 人员类别
INSERT INTO `person_category` (`category_name`, `category_code`, `description`, `sort_order`) VALUES
('涉恐涉暴人员', 'TERRORISM', '涉及恐怖主义、暴力活动人员', 1),
('涉稳人员', 'STABILITY', '涉及社会稳定人员', 2),
('刑事前科人员', 'CRIMINAL', '有刑事犯罪前科人员', 3),
('吸毒人员', 'DRUG', '吸毒或涉毒人员', 4),
('严重精神障碍患者', 'MENTAL', '严重精神障碍患者', 5),
('重点上访人员', 'PETITION', '重点信访人员', 6),
('其他重点关注人员', 'OTHER', '其他需要重点关注的人员', 7);

-- 系统用户 (密码均为: 123456, bcrypt hash)
INSERT INTO `sys_user` (`username`, `password`, `real_name`, `role`, `department_id`, `phone`) VALUES
('admin', '$2b$12$yBKJAsqqxln2KcE7giW1Uen3nO0C8V7VFceA0h.CaDlEn9WJnH84S', '系统管理员', 'admin', 1, '13800000001'),
('operator1', '$2b$12$yBKJAsqqxln2KcE7giW1Uen3nO0C8V7VFceA0h.CaDlEn9WJnH84S', '张三', 'operator', 2, '13800000002'),
('operator2', '$2b$12$yBKJAsqqxln2KcE7giW1Uen3nO0C8V7VFceA0h.CaDlEn9WJnH84S', '李四', 'operator', 3, '13800000003');

SET FOREIGN_KEY_CHECKS = 1;
