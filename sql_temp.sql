
CREATE TABLE `sym_file_incoming`(
    `relative_dir` VARCHAR(255) NOT NULL,
    `file_name` VARCHAR(128) NOT NULL,
    `last_event_type` CHAR(1) NOT NULL,
    `node_id` VARCHAR(50) NOT NULL,
    `file_modified_time` BIGINT,
    PRIMARY KEY (`relative_dir`(50), `file_name`(50))
);

CREATE TABLE `sym_file_snapshot`(
    `trigger_id` VARCHAR(128) NOT NULL,
    `router_id` VARCHAR(50) NOT NULL,
    `relative_dir` VARCHAR(255) NOT NULL,
    `file_name` VARCHAR(128) NOT NULL,
    `channel_id` VARCHAR(128) DEFAULT 'filesync' NOT NULL,
    `reload_channel_id` VARCHAR(128) DEFAULT 'filesync_reload' NOT NULL,
    `last_event_type` CHAR(1) NOT NULL,
    `crc32_checksum` BIGINT,
    `file_size` BIGINT,
    `file_modified_time` BIGINT,
    `last_update_time` DATETIME NOT NULL,
    `last_update_by` VARCHAR(50) NULL,
    `create_time` DATETIME NOT NULL,
    PRIMARY KEY (`trigger_id`, `router_id`, `relative_dir`(50), `file_name`(50)));


CREATE TABLE `sym_grouplet_link`(
    `grouplet_id` VARCHAR(50) NOT NULL,
    `external_id` VARCHAR(255) NOT NULL,
    `create_time` DATETIME NOT NULL,
    `last_update_by` VARCHAR(50) NULL,
    `last_update_time` DATETIME NOT NULL,
    PRIMARY KEY (`grouplet_id`, `external_id`(50))
);


CREATE TABLE `sym_parameter`(
    `external_id` VARCHAR(255) NOT NULL,
    `node_group_id` VARCHAR(50) NOT NULL,
    `param_key` VARCHAR(80) NOT NULL,
    `param_value` MEDIUMTEXT NULL,
    `create_time` DATETIME,
    `last_update_by` VARCHAR(50) NULL,
    `last_update_time` DATETIME,
    PRIMARY KEY (`external_id`(50), `node_group_id`, `param_key`(50))
);

CREATE TABLE `sym_registration_redirect`(
    `registrant_external_id` VARCHAR(255) NOT NULL,
    `registration_node_id` VARCHAR(50) NOT NULL,
    PRIMARY KEY (`registrant_external_id`(128))
);

CREATE TABLE `sym_registration_request`(
    `node_group_id` VARCHAR(50) NOT NULL,
    `external_id` VARCHAR(255) NOT NULL,
    `status` CHAR(2) NOT NULL,
    `host_name` VARCHAR(60) NOT NULL,
    `ip_address` VARCHAR(50) NOT NULL,
    `attempt_count` INTEGER DEFAULT 0,
    `registered_node_id` VARCHAR(50) NULL,
    `error_message` MEDIUMTEXT NULL,
    `create_time` DATETIME NOT NULL,
    `last_update_by` VARCHAR(50) NULL,
    `last_update_time` DATETIME NOT NULL,
    PRIMARY KEY (`node_group_id`, `external_id`(50), `create_time`)
);

CREATE INDEX `sym_idx_reg_req_1` ON `sym_registration_request` (`node_group_id`, `external_id`(50), `status`, `host_name`(50), `ip_address`(50));
