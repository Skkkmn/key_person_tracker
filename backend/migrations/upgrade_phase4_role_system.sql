-- ============================================================
-- 四级账号权限流转 - 数据库升级脚本 (Phase 4)
-- 1. 临时改为 VARCHAR 以解除 ENUM 约束
-- 2. 升级已有用户角色：admin -> super_admin
-- 3. 修改为新的 4 级 ENUM
-- ============================================================

USE key_person_mgmt;

ALTER TABLE `sys_user` MODIFY COLUMN `role` VARCHAR(20) NOT NULL DEFAULT 'operator' COMMENT '角色';

UPDATE `sys_user` SET `role` = 'super_admin' WHERE `role` = 'admin';

ALTER TABLE `sys_user`
  MODIFY COLUMN `role` ENUM('super_admin','dept_admin','operator','viewer') NOT NULL DEFAULT 'operator' COMMENT '角色';
