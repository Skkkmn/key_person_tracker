-- Phase 1: Data Foundation Enhancement
-- 1. Expand key_person table with new fields
ALTER TABLE key_person
  MODIFY COLUMN control_status VARCHAR(20) NOT NULL DEFAULT 'monitored',
  ADD COLUMN education VARCHAR(50) DEFAULT NULL AFTER photo_url,
  ADD COLUMN employment_status VARCHAR(50) DEFAULT NULL AFTER education,
  ADD COLUMN employer VARCHAR(200) DEFAULT NULL AFTER employment_status,
  ADD COLUMN political_status VARCHAR(20) DEFAULT NULL AFTER employer,
  ADD COLUMN ethnicity VARCHAR(20) DEFAULT NULL AFTER political_status,
  ADD COLUMN marital_status VARCHAR(20) DEFAULT NULL AFTER ethnicity,
  ADD COLUMN household_type VARCHAR(20) DEFAULT NULL AFTER marital_status,
  ADD COLUMN category_ext_fields JSON DEFAULT NULL AFTER case_description,
  ADD COLUMN archived_at DATETIME DEFAULT NULL AFTER updated_at,
  ADD COLUMN archived_by INT DEFAULT NULL AFTER archived_at,
  ADD COLUMN archive_reason TEXT DEFAULT NULL AFTER archived_by,
  ADD COLUMN lost_at DATETIME DEFAULT NULL AFTER archive_reason,
  ADD COLUMN lost_info TEXT DEFAULT NULL AFTER lost_at;

-- 2. Create tag table
CREATE TABLE IF NOT EXISTS `tag` (
  `tag_id` INT NOT NULL AUTO_INCREMENT,
  `tag_name` VARCHAR(50) NOT NULL,
  `tag_color` VARCHAR(20) DEFAULT '#409eff',
  `sort_order` INT DEFAULT 0,
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`tag_id`),
  UNIQUE KEY `uk_tag_name` (`tag_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 3. Create person_tag mapping table
CREATE TABLE IF NOT EXISTS `person_tag` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `person_id` INT NOT NULL,
  `tag_id` INT NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_person_tag` (`person_id`, `tag_id`),
  KEY `idx_tag_id` (`tag_id`),
  CONSTRAINT `fk_pt_person` FOREIGN KEY (`person_id`) REFERENCES `key_person` (`person_id`) ON DELETE CASCADE,
  CONSTRAINT `fk_pt_tag` FOREIGN KEY (`tag_id`) REFERENCES `tag` (`tag_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 4. Create operation_log table
CREATE TABLE IF NOT EXISTS `operation_log` (
  `log_id` BIGINT NOT NULL AUTO_INCREMENT,
  `user_id` INT DEFAULT NULL,
  `username` VARCHAR(50) DEFAULT NULL,
  `action` VARCHAR(30) NOT NULL,
  `entity_type` VARCHAR(30) NOT NULL,
  `entity_id` INT DEFAULT NULL,
  `entity_name` VARCHAR(200) DEFAULT NULL,
  `old_value` JSON DEFAULT NULL,
  `new_value` JSON DEFAULT NULL,
  `ip_address` VARCHAR(50) DEFAULT NULL,
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`log_id`),
  KEY `idx_user` (`user_id`),
  KEY `idx_action` (`action`),
  KEY `idx_entity` (`entity_type`, `entity_id`),
  KEY `idx_created` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 5. Create attachment table
CREATE TABLE IF NOT EXISTS `attachment` (
  `attachment_id` INT NOT NULL AUTO_INCREMENT,
  `entity_type` VARCHAR(30) NOT NULL,
  `entity_id` INT DEFAULT NULL,
  `file_name` VARCHAR(255) NOT NULL,
  `file_path` VARCHAR(500) NOT NULL,
  `file_size` INT DEFAULT 0,
  `mime_type` VARCHAR(100) DEFAULT NULL,
  `created_by` INT DEFAULT NULL,
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`attachment_id`),
  KEY `idx_entity` (`entity_type`, `entity_id`),
  KEY `idx_created_by` (`created_by`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 6. Insert default tags
INSERT INTO `tag` (`tag_name`, `tag_color`, `sort_order`) VALUES
('酗酒', '#e6a23c', 1),
('暴力倾向', '#f56c6c', 2),
('独居', '#909399', 3),
('无业', '#909399', 4),
('家庭矛盾', '#e6a23c', 5),
('网络涉险', '#f56c6c', 6),
('异地流动', '#409eff', 7),
('经济困难', '#e6a23c', 8),
('多次上访', '#f56c6c', 9),
('精神异常', '#f56c6c', 10);
