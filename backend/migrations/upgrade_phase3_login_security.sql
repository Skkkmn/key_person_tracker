-- ============================================================
-- 登录安全策略 - 数据库升级脚本 (Phase 3)
-- 为 sys_user 表新增登录安全相关字段
-- ============================================================

USE key_person_mgmt;

ALTER TABLE `sys_user`
  ADD COLUMN `login_attempts`      INT       DEFAULT 0  COMMENT '登录失败次数' AFTER `status`,
  ADD COLUMN `locked_until`        DATETIME  DEFAULT NULL COMMENT '锁定截止时间' AFTER `login_attempts`,
  ADD COLUMN `password_updated_at` DATETIME  DEFAULT NULL COMMENT '密码最后修改时间' AFTER `locked_until`;
