-- Phase 2: Core Business Features
-- 1. Visit tasks
CREATE TABLE IF NOT EXISTS `visit_task` (
  `task_id` INT NOT NULL AUTO_INCREMENT,
  `person_id` INT NOT NULL,
  `title` VARCHAR(200) NOT NULL,
  `description` TEXT,
  `task_type` VARCHAR(30) DEFAULT 'routine',
  `assigned_to` INT DEFAULT NULL,
  `assigned_by` INT DEFAULT NULL,
  `assign_time` DATETIME DEFAULT CURRENT_TIMESTAMP,
  `deadline` DATETIME,
  `status` VARCHAR(20) DEFAULT 'pending',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`task_id`),
  KEY `idx_person` (`person_id`),
  KEY `idx_assigned` (`assigned_to`),
  KEY `idx_status` (`status`),
  CONSTRAINT `fk_vt_person` FOREIGN KEY (`person_id`) REFERENCES `key_person` (`person_id`) ON DELETE CASCADE,
  CONSTRAINT `fk_vt_assigned` FOREIGN KEY (`assigned_to`) REFERENCES `sys_user` (`user_id`) ON DELETE SET NULL,
  CONSTRAINT `fk_vt_assigner` FOREIGN KEY (`assigned_by`) REFERENCES `sys_user` (`user_id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 2. Visit records
CREATE TABLE IF NOT EXISTS `visit_record` (
  `record_id` INT NOT NULL AUTO_INCREMENT,
  `task_id` INT DEFAULT NULL,
  `person_id` INT NOT NULL,
  `visitor_id` INT DEFAULT NULL,
  `visit_time` DATETIME NOT NULL,
  `location` VARCHAR(255),
  `longitude` DECIMAL(10,7),
  `latitude` DECIMAL(10,7),
  `content` TEXT,
  `performance` VARCHAR(50),
  `thought_dynamics` TEXT,
  `life_difficulty` TEXT,
  `has_abnormality` TINYINT(1) DEFAULT 0,
  `abnormality_desc` TEXT,
  `photo_urls` JSON,
  `audio_url` VARCHAR(500),
  `video_url` VARCHAR(500),
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`record_id`),
  KEY `idx_task` (`task_id`),
  KEY `idx_person` (`person_id`),
  KEY `idx_visitor` (`visitor_id`),
  CONSTRAINT `fk_vr_task` FOREIGN KEY (`task_id`) REFERENCES `visit_task` (`task_id`) ON DELETE SET NULL,
  CONSTRAINT `fk_vr_person` FOREIGN KEY (`person_id`) REFERENCES `key_person` (`person_id`) ON DELETE CASCADE,
  CONSTRAINT `fk_vr_visitor` FOREIGN KEY (`visitor_id`) REFERENCES `sys_user` (`user_id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 3. Risk assessments
CREATE TABLE IF NOT EXISTS `risk_assessment` (
  `assessment_id` INT NOT NULL AUTO_INCREMENT,
  `person_id` INT NOT NULL,
  `assessor_id` INT DEFAULT NULL,
  `previous_risk_level` VARCHAR(10),
  `new_risk_level` VARCHAR(10) NOT NULL,
  `score` INT DEFAULT 0,
  `score_details` JSON,
  `reason` TEXT,
  `is_auto` TINYINT(1) DEFAULT 0,
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`assessment_id`),
  KEY `idx_person` (`person_id`),
  CONSTRAINT `fk_ra_person` FOREIGN KEY (`person_id`) REFERENCES `key_person` (`person_id`) ON DELETE CASCADE,
  CONSTRAINT `fk_ra_assessor` FOREIGN KEY (`assessor_id`) REFERENCES `sys_user` (`user_id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 4. Notifications
CREATE TABLE IF NOT EXISTS `notification` (
  `notification_id` INT NOT NULL AUTO_INCREMENT,
  `title` VARCHAR(200) NOT NULL,
  `content` TEXT,
  `notification_type` VARCHAR(30) DEFAULT 'system',
  `sender_id` INT DEFAULT NULL,
  `receiver_id` INT DEFAULT NULL,
  `entity_type` VARCHAR(30),
  `entity_id` INT,
  `is_read` TINYINT(1) DEFAULT 0,
  `read_at` DATETIME,
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`notification_id`),
  KEY `idx_receiver` (`receiver_id`),
  KEY `idx_read` (`is_read`),
  KEY `idx_type` (`notification_type`),
  CONSTRAINT `fk_notif_sender` FOREIGN KEY (`sender_id`) REFERENCES `sys_user` (`user_id`) ON DELETE SET NULL,
  CONSTRAINT `fk_notif_receiver` FOREIGN KEY (`receiver_id`) REFERENCES `sys_user` (`user_id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 5. Lost contact tracking
CREATE TABLE IF NOT EXISTS `lost_contact_track` (
  `track_id` INT NOT NULL AUTO_INCREMENT,
  `person_id` INT NOT NULL,
  `lost_time` DATETIME,
  `last_location` VARCHAR(255),
  `search_measures` TEXT,
  `family_contact` TEXT,
  `progress` TEXT,
  `status` VARCHAR(20) DEFAULT 'tracking',
  `resolved_at` DATETIME,
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`track_id`),
  KEY `idx_person` (`person_id`),
  CONSTRAINT `fk_lct_person` FOREIGN KEY (`person_id`) REFERENCES `key_person` (`person_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 6. Alert extended fields for closed-loop workflow
ALTER TABLE person_alert
  ADD COLUMN `verify_result` TEXT DEFAULT NULL AFTER `handle_result`,
  ADD COLUMN `review_opinion` TEXT DEFAULT NULL AFTER `verify_result`,
  ADD COLUMN `reviewer_id` INT DEFAULT NULL AFTER `review_opinion`,
  ADD COLUMN `review_time` DATETIME DEFAULT NULL AFTER `reviewer_id`;
