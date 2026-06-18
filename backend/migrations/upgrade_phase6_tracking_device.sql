-- 手机定位追踪设备绑定表
CREATE TABLE IF NOT EXISTS tracking_device (
    device_id INT AUTO_INCREMENT PRIMARY KEY,
    person_id INT NOT NULL UNIQUE,
    device_name VARCHAR(100) DEFAULT '',
    device_imei VARCHAR(50) UNIQUE DEFAULT '',
    phone_number VARCHAR(20) DEFAULT '',
    api_token VARCHAR(64) NOT NULL UNIQUE,
    last_latitude DECIMAL(10, 7),
    last_longitude DECIMAL(10, 7),
    last_battery_level INT,
    last_online_at DATETIME,
    is_active TINYINT(1) DEFAULT 1,
    bound_by INT,
    bound_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (person_id) REFERENCES key_person(person_id) ON DELETE CASCADE,
    FOREIGN KEY (bound_by) REFERENCES sys_user(user_id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
