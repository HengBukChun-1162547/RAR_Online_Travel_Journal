SET FOREIGN_KEY_CHECKS = 0;

DROP VIEW IF EXISTS active_subscriptions;

DROP TABLE IF EXISTS journey_views;
DROP TABLE IF EXISTS achievement_progress;
DROP TABLE IF EXISTS user_achievements;
DROP TABLE IF EXISTS achievement_types;
DROP TABLE IF EXISTS support_comments;
DROP TABLE IF EXISTS user_appeals;
DROP TABLE IF EXISTS support_requests;
DROP TABLE IF EXISTS edit_notifications;
DROP TABLE IF EXISTS edit_logs;
DROP TABLE IF EXISTS followed_locations;
DROP TABLE IF EXISTS followed_users;
DROP TABLE IF EXISTS followed_journeys;
DROP TABLE IF EXISTS announcement_reads;
DROP TABLE IF EXISTS announcements;
DROP TABLE IF EXISTS event_images;
DROP TABLE IF EXISTS events;
DROP TABLE IF EXISTS journeys;
DROP TABLE IF EXISTS system_notifications;
DROP TABLE IF EXISTS free_trial_usage;
DROP TABLE IF EXISTS payments;
DROP TABLE IF EXISTS subscriptions;
DROP TABLE IF EXISTS subscription_plans;
DROP TABLE IF EXISTS locations;
DROP TABLE IF EXISTS role_permissions;
DROP TABLE IF EXISTS permissions;
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS roles;

SET FOREIGN_KEY_CHECKS = 1;


-- Roles and Permissions
CREATE TABLE roles (
    `role_id` INT AUTO_INCREMENT PRIMARY KEY,
    `role_name` VARCHAR(50) NOT NULL UNIQUE,
    `description` TEXT,
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Users
CREATE TABLE users (
	`user_id` int NOT NULL AUTO_INCREMENT,
	`username` varchar(20) NOT NULL,
	`password_hash` CHAR(60) NOT NULL,
	`email` varchar(320)  NOT NULL,
	`first_name` varchar(20) ,
	`last_name` varchar(20) ,
	`location` varchar(255),
	`profile_image` varchar(255),
	`description` text,
	`role_id` int NOT NULL DEFAULT 1,
	`status` enum('active','banned','restricted') NOT NULL DEFAULT 'active',
	PRIMARY KEY (`user_id`),
	UNIQUE KEY `username` (`username`),
	UNIQUE KEY `email` (`email`),
	CONSTRAINT fk_user_role
		FOREIGN KEY (role_id) REFERENCES roles(role_id)
		ON DELETE CASCADE
		ON UPDATE CASCADE
);

-- Roles and Permissions
CREATE TABLE permissions (
    `permission_id` INT AUTO_INCREMENT PRIMARY KEY,
    `permission_name` VARCHAR(100) NOT NULL UNIQUE,
    `description` TEXT,
    `category` VARCHAR(50),  -- For grouping permissions
    `type` VARCHAR(10),
    `is_default` BOOLEAN NOT NULL DEFAULT FALSE,
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE role_permissions (
    `role_id` INT NOT NULL,
    `permission_id` INT NOT NULL,
    `granted_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (role_id, permission_id),
    FOREIGN KEY (role_id) REFERENCES roles(role_id) ON DELETE CASCADE,
    FOREIGN KEY (permission_id) REFERENCES permissions(permission_id) ON DELETE CASCADE
);

-- Locations
CREATE TABLE locations (
	`location_id` int NOT NULL AUTO_INCREMENT,
	`name` varchar(255) NOT NULL,
	PRIMARY KEY (`location_id`),
	UNIQUE KEY `name` (`name`)
);

-- PREMIUMM FEATURES EPIC
CREATE TABLE subscription_plans (
    `subscription_plan_id` INT PRIMARY KEY AUTO_INCREMENT,
    `name` VARCHAR(50) NOT NULL,
    `duration_months` INT NOT NULL,
    `discount_percent` DECIMAL(5,2),
    `price_excl_gst` DECIMAL(10,2),
    `gst_percentage` DECIMAL(10,2),
    `subscription_type` ENUM('Trial', 'Purchased', 'Gifted') NOT NULL
);

CREATE TABLE subscriptions (
    `subscription_id` INT AUTO_INCREMENT PRIMARY KEY,
    `user_id` INT NOT NULL,
    `subscription_type` ENUM('Trial', 'Purchased', 'Gifted') NOT NULL,
    `subscription_plan_id` INT NOT NULL,
	`start_date` DATETIME NOT NULL,
	`expiry_date` DATETIME NOT NULL,
    `created_by` INT, -- NULL if purchased by user, user_id of admin if granted
	`note` VARCHAR(255) NULL,  -- the reason for gifting
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (created_by) REFERENCES users(user_id) ON DELETE SET NULL,
	FOREIGN KEY (subscription_plan_id) REFERENCES subscription_plans(subscription_plan_id)ON DELETE CASCADE
);

CREATE VIEW active_subscriptions AS
SELECT *, (expiry_date > NOW()) AS is_active
FROM subscriptions;

CREATE TABLE payments (
    `payment_id` INT AUTO_INCREMENT PRIMARY KEY,
    `subscription_id` INT NOT NULL,
    `payment_date` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `payment_method` VARCHAR(50) DEFAULT 'credit_card',
    `payment_amount` DECIMAL(10,2) NOT NULL,
    `card_number`  VARCHAR(19) NOT NULL,
	`card_cvv` VARCHAR(3) NOT NULL,
	`card_expiry_date` VARCHAR(7) NOT NULL,
    `card_holder` VARCHAR(100) NOT NULL,
    `card_type` VARCHAR(20) NOT NULL,
    `billing_country` VARCHAR(100) NOT NULL,
    `address1` VARCHAR(255) NOT NULL,
    `address2` VARCHAR(255) NULL,
    `city` VARCHAR(100) NOT NULL,
    `state` VARCHAR(100) NOT NULL,
    `postal` VARCHAR(20) NOT NULL,
    FOREIGN KEY (subscription_id) REFERENCES subscriptions(subscription_id) ON DELETE CASCADE
);

CREATE TABLE free_trial_usage (
    `user_id` INT PRIMARY KEY,
    `trial_used` BOOLEAN NOT NULL DEFAULT FALSE,
    `subscription_id` INT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (subscription_id) REFERENCES subscriptions(subscription_id) ON DELETE CASCADE
);

-- Journey
CREATE TABLE journeys (
	`journey_id` int NOT NULL AUTO_INCREMENT,
	`user_id` int NOT NULL,
	`title` varchar(255) NOT NULL,
	`description` text NOT NULL,
	`start_date` date NOT NULL,
	`create_time` datetime NOT NULL DEFAULT current_timestamp,
	`update_by` int,
	`update_time` datetime NOT NULL DEFAULT current_timestamp ON UPDATE current_timestamp,
	`status` enum('private','public','published') NOT NULL,
	`hidden` boolean NOT NULL DEFAULT FALSE,
	`no_edits` boolean NOT NULL DEFAULT FALSE,
	`cover_image` VARCHAR(255), -- For premium feature
	PRIMARY KEY (`journey_id`),
	CONSTRAINT fk_journey_user
		FOREIGN KEY (user_id) REFERENCES users(user_id)
		ON DELETE CASCADE
		ON UPDATE CASCADE,
	CONSTRAINT fk_journey_updater
		FOREIGN KEY (update_by) REFERENCES users(user_id)
		ON DELETE SET NULL
		ON UPDATE CASCADE
);

-- Event
CREATE TABLE events (
	`event_id` int NOT NULL AUTO_INCREMENT,
	`journey_id` int NOT NULL,
	`user_id` int NOT NULL,
	`location_id` int NOT NULL,
	`title` varchar(255) NOT NULL,
	`description` text,
	`start_date` datetime NOT NULL,
	`end_date` datetime,
	`create_time` datetime NOT NULL DEFAULT current_timestamp,
	`update_by` int,
	`update_time` datetime NOT NULL DEFAULT current_timestamp ON UPDATE current_timestamp,
	PRIMARY KEY (`event_id`),
	CONSTRAINT fk_event_user
		FOREIGN KEY (user_id) REFERENCES users(user_id)
		ON DELETE CASCADE
		ON UPDATE CASCADE,
	CONSTRAINT fk_event_journey
		FOREIGN KEY (journey_id) REFERENCES journeys(journey_id)
		ON DELETE CASCADE
		ON UPDATE CASCADE,
	CONSTRAINT fk_event_updater
		FOREIGN KEY (update_by) REFERENCES users(user_id)
		ON DELETE SET NULL
		ON UPDATE CASCADE,
	CONSTRAINT fk_event_location
		FOREIGN KEY (location_id) REFERENCES locations(location_id)
		ON DELETE NO ACTION
		ON UPDATE CASCADE
);

CREATE TABLE event_images (
    `image_id` INT NOT NULL AUTO_INCREMENT,
    `event_id` INT NOT NULL,
    `image_path` VARCHAR(255) NOT NULL,
    `upload_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (image_id),
    CONSTRAINT fk_event_images_event
        FOREIGN KEY (event_id) REFERENCES events(event_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

-- Announcement
CREATE TABLE announcements (
	`announcement_id` int NOT NULL AUTO_INCREMENT,
	`user_id` int NOT NULL,
	`title` varchar(255) NOT NULL,
	`description` text NOT NULL,
	`create_time` datetime NOT NULL DEFAULT current_timestamp,
	`update_by` int,
	`update_time` datetime DEFAULT current_timestamp ON UPDATE current_timestamp,
	PRIMARY KEY (`announcement_id`),
	CONSTRAINT fk_announcement_user
		FOREIGN KEY (user_id) REFERENCES users(user_id)
		ON DELETE NO ACTION
		ON UPDATE CASCADE,
	CONSTRAINT fk_announcement_updater
		FOREIGN KEY (update_by) REFERENCES users(user_id)
		ON DELETE SET NULL
		ON UPDATE CASCADE
);

CREATE TABLE announcement_reads (
    `announcement_read_id` INT NOT NULL AUTO_INCREMENT,
    `user_id` INT NOT NULL,
    `announcement_id` INT NOT NULL,
    `read_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (announcement_read_id),
    UNIQUE KEY unique_user_announcement (user_id, announcement_id),
    CONSTRAINT fk_read_user
        FOREIGN KEY (user_id) REFERENCES users(user_id)
        ON DELETE CASCADE,
    CONSTRAINT fk_read_announcement
        FOREIGN KEY (announcement_id) REFERENCES announcements(announcement_id)
        ON DELETE CASCADE
);

-- DEPARTURE BOARD EPIC
CREATE TABLE followed_journeys (
    `followed_journey_id` INT NOT NULL AUTO_INCREMENT,
    `follower_id` INT NOT NULL,
    `journey_id` INT NOT NULL,
    `followed_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (followed_journey_id),
    UNIQUE KEY unique_user_journey (follower_id, journey_id),
    CONSTRAINT fk_follow_journey_user
        FOREIGN KEY (follower_id) REFERENCES users(user_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    CONSTRAINT fk_follow_journey
        FOREIGN KEY (journey_id) REFERENCES journeys(journey_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

CREATE TABLE followed_users (
    `followed_user_id` INT NOT NULL AUTO_INCREMENT,
    `follower_id` INT NOT NULL,
    `followed_id` INT NOT NULL,
    `followed_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (followed_user_id),
    UNIQUE KEY unique_follower_followed (follower_id, followed_id),
    CONSTRAINT fk_follower
        FOREIGN KEY (follower_id) REFERENCES users(user_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    CONSTRAINT fk_followed
        FOREIGN KEY (followed_id) REFERENCES users(user_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

CREATE TABLE followed_locations (
    `followed_location_id` INT NOT NULL AUTO_INCREMENT,
    `follower_id` INT NOT NULL,
    `location_id` INT NOT NULL,
    `followed_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (followed_location_id),
    UNIQUE KEY unique_user_location (follower_id, location_id),
    CONSTRAINT fk_follow_location_user
        FOREIGN KEY (follower_id) REFERENCES users(user_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    CONSTRAINT fk_follow_location
        FOREIGN KEY (location_id) REFERENCES locations(location_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

-- ADVANCED EDITING EPIC
CREATE TABLE edit_logs (
    `edit_log_id` INT NOT NULL AUTO_INCREMENT,
    `journey_id` INT,
    `event_id` INT,
    `editor_id` INT NOT NULL,
    `edit_reason` TEXT NOT NULL,
    `summary` TEXT NOT NULL, -- title: original -> changed; image: removed;
    `edited_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (edit_log_id),
    CONSTRAINT fk_log_journey
        FOREIGN KEY (journey_id) REFERENCES journeys(journey_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    CONSTRAINT fk_log_event
        FOREIGN KEY (event_id) REFERENCES events(event_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    CONSTRAINT fk_log_editor
        FOREIGN KEY (editor_id) REFERENCES users(user_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

-- NOTIFICATIONS
CREATE TABLE edit_notifications (
    `notification_id` INT AUTO_INCREMENT PRIMARY KEY,
    `user_id` INT NOT NULL,
    `edit_log_id` INT NOT NULL,
    `is_read` BOOLEAN NOT NULL DEFAULT FALSE,
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_edit_notify_user
        FOREIGN KEY (user_id) REFERENCES users(user_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    CONSTRAINT fk_edit_notify_log
        FOREIGN KEY (edit_log_id) REFERENCES edit_logs(edit_log_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

CREATE TABLE system_notifications(
    `notification_id` INT AUTO_INCREMENT PRIMARY KEY,
    `type` ENUM('Subscription','Gift','Achievement') NOT NULL,
    `user_id` INT NOT NULL,
    `message` VARCHAR(255) NOT NULL,
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `is_read` BOOLEAN NOT NULL DEFAULT FALSE,
    CONSTRAINT fk_system_user_id
        FOREIGN KEY (user_id) REFERENCES users(user_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

-- HELPDESK EPIC
CREATE TABLE support_requests (
    `request_id` INT AUTO_INCREMENT PRIMARY KEY,
    `user_id` INT NOT NULL,
    `issue_type` ENUM('Bug', 'Help_Request', 'Appeal', 'Others') NOT NULL,
    `summary` VARCHAR(255) NOT NULL,
    `description` TEXT NOT NULL,
    `screenshot_path` VARCHAR(255),
    `status` ENUM('New', 'Open', 'Stalled', 'Resolved') NOT NULL DEFAULT 'New',
    `assignee_id` INT,
    `priority` ENUM('Normal', 'High') NOT NULL DEFAULT 'Normal',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_support_user
        FOREIGN KEY (user_id) REFERENCES users(user_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    CONSTRAINT fk_support_assignee
        FOREIGN KEY (assignee_id) REFERENCES users(user_id)
        ON DELETE SET NULL
        ON UPDATE CASCADE
);

CREATE TABLE support_comments (
    `comment_id` INT AUTO_INCREMENT PRIMARY KEY,
    `request_id` INT NOT NULL,
    `user_id` INT NOT NULL,
    `comment` TEXT NOT NULL,
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_support_comment_request
        FOREIGN KEY (request_id) REFERENCES support_requests(request_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    CONSTRAINT fk_support_comment_user
        FOREIGN KEY (user_id) REFERENCES users(user_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

CREATE TABLE user_appeals (
    `appeal_id` INT AUTO_INCREMENT PRIMARY KEY,
    `user_id` INT NOT NULL,
    `appeal_type` ENUM('Hidden_Journey', 'Restricted_Sharing', 'Site_Ban') NOT NULL,
    `journey_id` INT,
    `reason` TEXT NOT NULL,
    `status` ENUM('Pending', 'Approved', 'Rejected') NOT NULL DEFAULT 'Pending',
    `reviewer_id` INT,
    `response` TEXT,
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_appeal_user
        FOREIGN KEY (user_id) REFERENCES users(user_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    CONSTRAINT fk_appeal_journey
        FOREIGN KEY (journey_id) REFERENCES journeys(journey_id)
        ON DELETE SET NULL
        ON UPDATE CASCADE,
    CONSTRAINT fk_appeal_reviewer
        FOREIGN KEY (reviewer_id) REFERENCES users(user_id)
        ON DELETE SET NULL
        ON UPDATE CASCADE
);

-- GAMIFICATION EPIC
CREATE TABLE achievement_types (
    `achievement_type_id` INT AUTO_INCREMENT PRIMARY KEY,
    `title` VARCHAR(100) NOT NULL UNIQUE,
    `description` TEXT NOT NULL,
    `points` INT NOT NULL DEFAULT 1,
    `icon_path` VARCHAR(255),
    `is_premium` BOOLEAN NOT NULL DEFAULT FALSE,
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE user_achievements (
    `user_achievement_id` INT AUTO_INCREMENT PRIMARY KEY,
    `user_id` INT NOT NULL,
    `achievement_type_id` INT NOT NULL,
    `unlocked_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_achievement_user
        FOREIGN KEY (user_id) REFERENCES users(user_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    CONSTRAINT fk_achievement_type
        FOREIGN KEY (achievement_type_id) REFERENCES achievement_types(achievement_type_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

CREATE TABLE achievement_progress (
    `achievement_progress_id` INT AUTO_INCREMENT PRIMARY KEY,
    `user_id` INT NOT NULL,
    `achievement_type_id` INT NOT NULL,
    `current_value` INT NOT NULL DEFAULT 0,
    `target_value` INT NOT NULL,
    `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY user_achievement_type (user_id, achievement_type_id),
    CONSTRAINT fk_progress_user
        FOREIGN KEY (user_id) REFERENCES users(user_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    CONSTRAINT fk_progress_achievement
        FOREIGN KEY (achievement_type_id) REFERENCES achievement_types(achievement_type_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

CREATE TABLE journey_views (
    `view_id` INT AUTO_INCREMENT PRIMARY KEY,
    `user_id` INT NOT NULL,
    `journey_id` INT NOT NULL,
    `journey_status` enum('private','public','published') NOT NULL,
    `viewed_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY unique_user_journey_view (user_id, journey_id),
    CONSTRAINT fk_view_user
        FOREIGN KEY (user_id) REFERENCES users(user_id)
        ON DELETE CASCADE,
    CONSTRAINT fk_view_journey
        FOREIGN KEY (journey_id) REFERENCES journeys(journey_id)
        ON DELETE CASCADE
);