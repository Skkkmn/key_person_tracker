-- ============================================================
-- 异地流入流出推送 - 数据库升级脚本 (Phase 5)
-- 新建 cross_region_track 表
-- ============================================================

USE key_person_mgmt;

DROP TABLE IF EXISTS `cross_region_track`;
CREATE TABLE `cross_region_track` (
  `track_id`       INT          NOT NULL AUTO_INCREMENT,
  `person_id`      INT          NOT NULL COMMENT '关联重点人员ID',
  `direction`      VARCHAR(10)  NOT NULL COMMENT '流动方向 in=流入 out=流出',
  `from_dept_id`   INT                   DEFAULT NULL COMMENT '来源部门ID',
  `to_dept_id`     INT                   DEFAULT NULL COMMENT '目标部门ID',
  `detected_at`    DATETIME     NOT NULL COMMENT '发现时间',
  `detected_by`    INT                   DEFAULT NULL COMMENT '发现人',
  `notify_dept_id` INT                   DEFAULT NULL COMMENT '推送部门ID',
  `notified`       TINYINT      NOT NULL DEFAULT 0 COMMENT '是否已推送通知',
  `notified_at`    DATETIME              DEFAULT NULL COMMENT '推送时间',
  `status`         VARCHAR(20)  NOT NULL DEFAULT 'pending' COMMENT '状态 pending待处理 confirmed已确认 dismissed已忽略',
  `remark`         TEXT                  DEFAULT NULL COMMENT '备注',
  `created_at`     DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at`     DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`track_id`),
  KEY `idx_person_id` (`person_id`),
  KEY `idx_from_dept` (`from_dept_id`),
  KEY `idx_to_dept` (`to_dept_id`),
  KEY `idx_direction` (`direction`),
  KEY `idx_status` (`status`),
  CONSTRAINT `fk_cross_region_person` FOREIGN KEY (`person_id`) REFERENCES `key_person` (`person_id`) ON DELETE CASCADE,
  CONSTRAINT `fk_cross_region_from_dept` FOREIGN KEY (`from_dept_id`) REFERENCES `department` (`dept_id`) ON DELETE SET NULL,
  CONSTRAINT `fk_cross_region_to_dept` FOREIGN KEY (`to_dept_id`) REFERENCES `department` (`dept_id`) ON DELETE SET NULL,
  CONSTRAINT `fk_cross_region_detector` FOREIGN KEY (`detected_by`) REFERENCES `sys_user` (`user_id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='异地流入流出记录';
