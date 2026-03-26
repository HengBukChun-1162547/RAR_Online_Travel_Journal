-- Drop schema if it exists, then create it
DROP database IF EXISTS onlinetravel;

CREATE DATABASE onlinetravel;
use onlinetravel;

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

--
INSERT INTO roles (role_name, description) VALUES
('traveller', 'Regular user who can create, edit, and share their own travel journal'),
('editor', 'Staff member who can edit content in public journeys'),
('admin', 'Administrator with full system access'),
('premium', 'Premium user with access to additional features and content'),
('trial', 'User with a trial subscription'),
('support_tech', 'Customer support staff who can assist users with technical issues');


INSERT INTO users (user_id, username, password_hash, email, first_name, last_name, `location`, profile_image, `description`, `role_id`, `status`) VALUES
(1, 'Traveller1', '$2b$12$N1jOZLuC3BCV2HNBre4M6ODisuhKgTtESjdvSW.QkpuEbIFnBW0im', 'traveller1@example.com', 'Ava', 'Taylor', NULL, 'uploads/profile/Traveller1.jpeg', NULL, '1', 'active'),
(2, 'Traveller2', '$2b$12$vyaPiC6JSgpO6Q.UgQvSJ.4LfHoGCb34x1K36Wg0N5IVHQaL.9NB6', 'traveller2@example.com', 'James', 'White', NULL, 'uploads/profile/Traveller2.jpeg', NULL, '1', 'active'),
(3, 'Traveller3', '$2b$12$TtH6Wn6TUD0jECwZFW4Zw.CNv4EeNed9F0puw9qVwfHV4NqKWtFgG', 'traveller3@example.com', 'Sophia', 'Hall', NULL, 'uploads/profile/Traveller3.jpeg', NULL, '1', 'active'),
(4, 'Traveller4', '$2b$12$TtH6Wn6TUD0jECwZFW4Zw.CNv4EeNed9F0puw9qVwfHV4NqKWtFgG', 'traveller4@example.com', 'Mia', 'King', NULL, 'uploads/profile/Traveller4.jpeg', NULL, '1', 'active'),
(5, 'Traveller5', '$2b$12$TtH6Wn6TUD0jECwZFW4Zw.CNv4EeNed9F0puw9qVwfHV4NqKWtFgG', 'traveller5@example.com', 'Henry', 'Scott', NULL, 'uploads/profile/Traveller5.jpeg', NULL, '1', 'active'),
(6, 'Traveller6', '$2b$12$TtH6Wn6TUD0jECwZFW4Zw.CNv4EeNed9F0puw9qVwfHV4NqKWtFgG', 'traveller6@example.com', 'Isabella', 'Adams', NULL, 'uploads/profile/Traveller6.jpeg', NULL, '1', 'active'),
(7, 'Traveller7', '$2b$12$TtH6Wn6TUD0jECwZFW4Zw.CNv4EeNed9F0puw9qVwfHV4NqKWtFgG', 'traveller7@example.com', 'Alexander', 'Baker', NULL, 'uploads/profile/Traveller7.jpeg', NULL, '1', 'active'),
(8, 'Traveller8', '$2b$12$TtH6Wn6TUD0jECwZFW4Zw.CNv4EeNed9F0puw9qVwfHV4NqKWtFgG', 'traveller8@example.com', 'Charlotte', 'Nelson', NULL, 'uploads/profile/Traveller8.jpeg', NULL, '1', 'banned'),
(9, 'Traveller9', '$2b$12$TtH6Wn6TUD0jECwZFW4Zw.CNv4EeNed9F0puw9qVwfHV4NqKWtFgG', 'traveller9@example.com', 'William', 'Hill', NULL, 'uploads/profile/Traveller9.jpeg', NULL, '1', 'active'),
(10, 'Traveller10', '$2b$12$TtH6Wn6TUD0jECwZFW4Zw.CNv4EeNed9F0puw9qVwfHV4NqKWtFgG', 'traveller10@example.com', 'Amelia', 'Ward', NULL, 'uploads/profile/Traveller10.jpeg', NULL, '1', 'active'),
(11, 'Traveller11', '$2b$12$TtH6Wn6TUD0jECwZFW4Zw.CNv4EeNed9F0puw9qVwfHV4NqKWtFgG', 'traveller11@example.com', 'Benjamin', 'Brooks', NULL, 'uploads/profile/Traveller11.jpeg', NULL, '4', 'active'),
(12, 'Traveller12', '$2b$12$TtH6Wn6TUD0jECwZFW4Zw.CNv4EeNed9F0puw9qVwfHV4NqKWtFgG', 'traveller12@example.com', 'Harper', 'Gray', NULL, 'uploads/profile/Traveller12.jpeg', NULL, '4', 'active'),
(13, 'Traveller13', '$2b$12$TtH6Wn6TUD0jECwZFW4Zw.CNv4EeNed9F0puw9qVwfHV4NqKWtFgG', 'traveller13@example.com', 'Daniel', 'Reed', NULL, 'uploads/profile/Traveller13.jpeg', NULL, '4', 'active'),
(14, 'Traveller14', '$2b$12$TtH6Wn6TUD0jECwZFW4Zw.CNv4EeNed9F0puw9qVwfHV4NqKWtFgG', 'traveller14@example.com', 'Evelyn', 'Price', NULL, 'uploads/profile/Traveller14.jpeg', NULL, '4', 'active'),
(15, 'Traveller15', '$2b$12$TtH6Wn6TUD0jECwZFW4Zw.CNv4EeNed9F0puw9qVwfHV4NqKWtFgG', 'traveller15@example.com', 'Matthew', 'Cox', NULL, 'uploads/profile/Traveller15.jpeg', NULL, '4', 'active'),
(16, 'Traveller16', '$2b$12$TtH6Wn6TUD0jECwZFW4Zw.CNv4EeNed9F0puw9qVwfHV4NqKWtFgG', 'traveller16@example.com', 'Ella', 'Richardson', NULL, 'uploads/profile/Traveller16.jpeg', NULL, '5', 'active'),
(17, 'Traveller17', '$2b$12$TtH6Wn6TUD0jECwZFW4Zw.CNv4EeNed9F0puw9qVwfHV4NqKWtFgG', 'traveller17@example.com', 'Joseph', 'Howard', NULL, 'uploads/profile/Traveller17.jpeg', NULL, '5', 'active'),
(18, 'Traveller18', '$2b$12$TtH6Wn6TUD0jECwZFW4Zw.CNv4EeNed9F0puw9qVwfHV4NqKWtFgG', 'traveller18@example.com', 'Avery', 'Cook', NULL, 'uploads/profile/Traveller18.jpeg', NULL, '5', 'restricted'),
(19, 'Traveller19', '$2b$12$TtH6Wn6TUD0jECwZFW4Zw.CNv4EeNed9F0puw9qVwfHV4NqKWtFgG', 'traveller19@example.com', 'Samuel', 'Bell', NULL, 'uploads/profile/Traveller19.jpeg', NULL, '5', 'active'),
(20, 'Traveller20', '$2b$12$TtH6Wn6TUD0jECwZFW4Zw.CNv4EeNed9F0puw9qVwfHV4NqKWtFgG', 'traveller20@example.com', 'Luna', 'Murphy', NULL, 'uploads/profile/Traveller20.jpeg', NULL, '5', 'active'),
(21, 'Admin1', '$2b$12$Cir.3xvp4leUzGXd46/E1uFhR24enxcjyHK79eWB3TBYW3naYOtJG', 'admin1@example.com', 'Liam', 'Walker', NULL, 'uploads/profile/Pokeball.png', NULL, '3', 'active'),
(22, 'Admin2', '$2b$12$9fZXoHA4altbTOIDWpCquuYvyITa06f9NZTKKmgMKvtqJozdrGStO', 'admin2@example.com', 'Emma', 'Roberts', NULL, 'uploads/profile/Pokeball.png', NULL, '3', 'active'),
(23, 'Admin3', '$2b$12$9fZXoHA4altbTOIDWpCquuYvyITa06f9NZTKKmgMKvtqJozdrGStO', 'admin3@example.com', 'Logan', 'Long', NULL, 'uploads/profile/Pokeball.png', NULL, '3', 'active'),
(24, 'Admin4', '$2b$12$9fZXoHA4altbTOIDWpCquuYvyITa06f9NZTKKmgMKvtqJozdrGStO', 'admin4@example.com', 'Grace', 'Ramirez', NULL, 'uploads/profile/Pokeball.png', NULL, '3', 'active'),
(25, 'Admin5', '$2b$12$9fZXoHA4altbTOIDWpCquuYvyITa06f9NZTKKmgMKvtqJozdrGStO', 'admin5@example.com', 'Tyler', 'Moore', NULL, 'uploads/profile/Pokeball.png', NULL, '3', 'active'),
(26, 'Editor1', '$2b$12$METPRgw1b/OOC8cJgRwknuYw1OXVkVm2bIxOnmQtR16MRXXsg3Dym', 'editor1@example.com', 'Noah', 'Smith', NULL, 'uploads/profile/Eagle.png', NULL, '2', 'active'),
(27, 'Editor2', '$2b$12$b0RCfEO3xxMpHLGoMtF2YuweoAoemRarMQVcdiE5yVJkxZIVYL9j2', 'editor2@example.com', 'Olivia', 'Johnson', NULL, 'uploads/profile/Eagle.png', NULL, '2', 'active'),
(28, 'Editor3', '$2b$12$Q9Y7BiewuE9Pb6tem9BFkuD9uI5QDme.8EHLdVzx5wOfjzV2pN0Ba', 'editor3@example.com', 'Elijah', 'Brown', NULL, 'uploads/profile/Eagle.png', NULL, '2', 'active'),
(29, 'Editor4', '$2b$12$Q9Y7BiewuE9Pb6tem9BFkuD9uI5QDme.8EHLdVzx5wOfjzV2pN0Ba', 'editor4@example.com', 'David', 'Bailey', NULL, 'uploads/profile/Eagle.png', NULL, '2', 'active'),
(30, 'Editor5', '$2b$12$Q9Y7BiewuE9Pb6tem9BFkuD9uI5QDme.8EHLdVzx5wOfjzV2pN0Ba', 'editor5@example.com', 'Scarlett', 'Perry', NULL, 'uploads/profile/Eagle.png', NULL, '2', 'active'),
(31, 'SupportTech1', '$2b$12$TtH6Wn6TUD0jECwZFW4Zw.CNv4EeNed9F0puw9qVwfHV4NqKWtFgG', 'supporttech1@example.com', 'Lucas', 'Allen', NULL, 'uploads/profile/Squirtle.png', NULL, '6', 'active'),
(32, 'SupportTech2', '$2b$12$TtH6Wn6TUD0jECwZFW4Zw.CNv4EeNed9F0puw9qVwfHV4NqKWtFgG', 'supporttech2@example.com', 'Jackson', 'Cooper', NULL, 'uploads/profile/Squirtle.png', NULL, '6', 'active'),
(33, 'SupportTech3', '$2b$12$TtH6Wn6TUD0jECwZFW4Zw.CNv4EeNed9F0puw9qVwfHV4NqKWtFgG', 'supporttech3@example.com', 'Chloe', 'Barnes', NULL, 'uploads/profile/Squirtle.png', NULL, '6', 'active'),
(34, 'SupportTech4', '$2b$12$TtH6Wn6TUD0jECwZFW4Zw.CNv4EeNed9F0puw9qVwfHV4NqKWtFgG', 'supporttech4@example.com', 'Sebastian', 'Powell', NULL, 'uploads/profile/Squirtle.png', NULL, '6', 'active'),
(35, 'SupportTech5', '$2b$12$TtH6Wn6TUD0jECwZFW4Zw.CNv4EeNed9F0puw9qVwfHV4NqKWtFgG', 'supporttech5@example.com', 'Brian', 'Carter', NULL, 'uploads/profile/Squirtle.png', NULL, '6', 'active'),
(36, 'Testuser1', '$2b$12$TtH6Wn6TUD0jECwZFW4Zw.CNv4EeNed9F0puw9qVwfHV4NqKWtFgG', 'testuser1@example.com', 'Alexander', 'Johnson', NULL, NULL, NULL, '1', 'active'),
(37, 'Testuser2', '$2b$12$TtH6Wn6TUD0jECwZFW4Zw.CNv4EeNed9F0puw9qVwfHV4NqKWtFgG', 'testuser2@example.com', 'Sophia', 'Williams', NULL, NULL, NULL, '4', 'active'),
(38, 'Will1', '$2b$12$TtH6Wn6TUD0jECwZFW4Zw.CNv4EeNed9F0puw9qVwfHV4NqKWtFgG', 'will1@example.com', 'Will', 'Williams', NULL, NULL, NULL, '1', 'active'),
(39, 'Will2', '$2b$12$TtH6Wn6TUD0jECwZFW4Zw.CNv4EeNed9F0puw9qVwfHV4NqKWtFgG', 'will2@example.com', 'Well', 'Williams', NULL, NULL, NULL, '1', 'active');

INSERT INTO permissions (permission_name, description, category, type, is_default) VALUES
-- landing
('view_landing_page', 'Can view the landing page', 'landing', 'access', 1),
-- Profile permissions
('view_own_profile', 'Can view own user profile', 'profile', 'access', 1),
('edit_own_profile', 'Can edit own user profile', 'profile', 'action', 1),
('change_own_password', 'Can change own password', 'profile', 'action', 1),
('view_others_profile', 'Can view other users profiles', 'profile', 'access', 0),
('edit_others_profile', 'Can edit other users profiles', 'profile', 'action', 0),
('view_others_public_profile', 'Can view other users public profiles', 'profile', 'access', 1),
('view_others_public_profile_map', 'Can view other users public profiles', 'profile', 'access', 0),
-- Journey permissions
('create_own_journey', 'Can create new journeys', 'journey', 'action', 1),
('edit_own_journey', 'Can edit own journeys', 'journey', 'action', 1),
('delete_own_journey', 'Can delete own journeys', 'journey', 'action', 1),
('view_own_journey', 'Can view own journeys (including private)', 'journey', 'access', 1),
('share_journey', 'Can share journeys publicly', 'journey', 'action', 0),
('edit_others_puclic_journey', 'Can edit other users public journeys', 'journey', 'action', 0),
('delete_others_puclic_journey', 'Can delete other users public journeys', 'journey', 'action', 0),
('view_others_puclic_journey', 'Can view other users public journeys', 'journey', 'access', 1),
('edit_others_published_journey', 'Can edit other users published journeys', 'journey', 'action', 0),
('delete_others_published_journey', 'Can delete other users published journeys', 'journey', 'action', 0),
('view_others_published_journey', 'Can view other users published journeys', 'journey', 'access', 1),
('edit_others_private_journey', 'Can edit other users private journeys', 'journey', 'action', 0),
('delete_others_private_journey', 'Can delete other private journeys', 'journey', 'action', 0),
('view_others_private_journey', 'Can view other users private journeys', 'journey', 'access', 0),
('hide_journey', 'Can hide inappropriate public journeys', 'journey', 'action', 0),
('publish_journey', 'Can publish journeys to homepage (premium)', 'journey', 'action', 0),
('view_hidden_journey', 'Can view hidden journeys', 'journey', 'access', 0),
('create_journey_cover', 'Can create a cover of journey', 'journey', 'access', 0),
('delete_journey_cover', 'Can delete a cover of journey', 'journey', 'access', 1),
-- Event permissions
('create_own_event', 'Can create events in own journeys', 'event', 'action', 1),
('edit_own_event', 'Can edit own events', 'event', 'action', 1),
('delete_own_event', 'Can delete own events', 'event', 'action', 1),
('view_own_event', 'Can view own events', 'event', 'access', 1),
('add_single_photo', 'Can add a single photo to an event', 'event', 'action', 1),
('add_multiple_photos', 'Can add multiple photos to an event (premium)', 'event', 'action', 0),
('edit_others_public_event', 'Can edit events in other users public journeys', 'event', 'action', 1),
('delete_others_public_event', 'Can delete events in other users public journeys', 'event', 'action', 1),
('view_others_public_event', 'Can view events in other users public journeys', 'event', 'access', 1),
('edit_others_private_event', 'Can edit events in other users private journeys', 'event', 'action', 0),
('delete_others_private_event', 'Can delete events in other users private journeys', 'event', 'action', 0),
('view_others_private_event', 'Can view events in other users private journeys', 'event', 'access', 0),
('edit_others_published_event', 'Can edit events in other users published journeys', 'event', 'action', 0),
('delete_others_published_event', 'Can delete events in other users published journeys', 'event', 'action', 0),
('view_others_published_event', 'Can view events in other users published journeys', 'event', 'access', 1),
('remove_others_photos', 'Can remove photos from other users events', 'event', 'action', 0),
-- Location permissions
('manage_locations', 'Can manage and standardize locations', 'location', 'action', 0),
-- User management permissions
('view_user_management', 'Can access the user management pages', 'user_management', 'access', 0),
('update_user_status', 'Can update user active status', 'user_management', 'action', 0),
('update_user_sharing', 'Can prevent users from sharing journeys (active/restricted)', 'user_management', 'action', 0),
('update_roles', 'Can change user roles', 'user_management', 'action', 0),
-- Announcement permissions
('view_announcements', 'Can create system announcements', 'announcement', 'access', 1),
('create_announcements', 'Can create system announcements', 'announcement', 'action', 0),
('edit_announcements', 'Can edit system announcements', 'announcement', 'action', 0),
('delete_announcements', 'Can delete system announcements', 'announcement', 'action', 0),
-- System notification
('view_own_system_notification', 'Can view own system notification', 'system_notification', 'access', 1),
('view_others_system_notification', 'Can view others system notification', 'system_notification', 'access', 0),
('view_edit_log_notification', 'Can view edit log notification', 'notification', 'access', 1),
-- Departure Board
('view_departure_board', 'Can view departure board', 'departure_board', 'access', 0),
('follow_journey', 'Can follow journeys', 'departure_board', 'access', 0),
('follow_user', 'Can follow users', 'departure_board', 'access', 0),
('follow_location', 'Can follow follow_locations', 'departure_board', 'access', 0),
-- Edit Log
('view_own_edit_log', 'Can view own edit log', 'edit_log', 'access', 0),
('view_others_edit_log', 'Can view others edit log', 'edit_log', 'access', 0),
('create_edit_log', 'Can create an edit log', 'edit_log', 'action', 0),
-- No Edits Flag
('create_no_edits_flag', 'Can create no edits flag', 'no_edits_flag', 'action', 0),
('view_own_no_edits_flag', 'Can view own no edits flag', 'no_edits_flag', 'action', 0),
('view_others_no_edits_flag', 'Can view others no edits flag', 'no_edits_flag', 'action', 0),
-- Helpdesk
('view_request', 'Can view a request', 'helpdesk', 'action', 1),
('create_request', 'Can create a request', 'helpdesk', 'action', 1),
('take_request', 'Can take a request', 'helpdesk', 'action', 0),
('drop_request', 'Can drop a request', 'helpdesk', 'action', 0),
-- Gamification
('view_general_achievements', 'Can view general achievements', 'gamification', 'access', 1),
('view_premium_achievements', 'Can view premium achievements', 'gamification', 'access', 0),
('view_leader_board', 'Can view leader board', 'gamification', 'access', 1),
-- Premium features
('view_premium_features', 'Can view premium features', 'premium', 'access', 1),
('view_subscription_page', 'Can view subscription page', 'premium', 'access', 1),
('view_payment_page', 'Can view payment page', 'premium', 'access', 1),
('view_own_subscriptions', 'Can view own subscription records', 'premium', 'access', 0),
('view_own_payments', 'Can view own payment records', 'premium', 'access', 0),
('view_others_subscriptions', 'Can view others subscription records', 'premium', 'access', 0),
('view_others_payments', 'Can view others payment records', 'premium', 'access', 0),
('view_trial_page', 'Can view trial page', 'premium', 'access', 0),
('view_reward_page', 'Can view reward page', 'premium', 'access', 0),
('create_subscription', 'Can create subscription', 'premium', 'action', 0),
('create_trial', 'Can create trial', 'premium', 'action', 0),
('create_gift', 'Can create gift', 'premium', 'action', 0),
('receive_gift', 'Can receive gift', 'premium', 'action', 0),
('use_premium_features', 'Can use premium features', 'premium', 'action', 0);

-- Traveller permissions
INSERT INTO role_permissions (role_id, permission_id)
SELECT 1, permission_id FROM permissions WHERE is_default = TRUE
UNION
SELECT 1, permission_id FROM permissions WHERE permission_name IN (
    'view_trial_page',
    'create_subscription',
    'create_trial',
    'receive_gift',
    'view_subscription_expired_notification'
) AND is_default = FALSE;
-- Editor permissions
INSERT INTO role_permissions (role_id, permission_id)
SELECT 2, permission_id FROM permissions WHERE is_default = TRUE
UNION
SELECT 2, permission_id FROM permissions WHERE permission_name IN (
    'edit_others_puclic_journey',
    'edit_others_published_journey',
    'hide_journey',
    'edit_others_public_event',
    'edit_others_published_event',
    'remove_others_photos',
    'manage_locations',
    'create_announcements',
    'edit_announcements',
    'delete_announcements',
    'share_journey',
    'publish_journey',
    'add_multiple_photos',
    'update_user_sharing',
	'view_hidden_journey',
	'view_own_edit_log',
	'view_others_edit_log',
	'create_edit_log',
	'view_others_public_profile_map',
	'view_own_subscriptions',
	'view_own_payments',
	'view_others_subscriptions',
	'view_others_payments',
	'view_premium_achievements',
	'follow_journey',
	'follow_user',
	'follow_location',
	'take_request',
	'drop_request',
    'view_departure_board',
    'use_premium_features',
    'create_no_edits_flag',
    'view_own_no_edits_flag',
    'view_others_no_edits_flag'
) AND is_default = FALSE;
-- Admin permissions
INSERT INTO role_permissions (role_id, permission_id)
SELECT 3, permission_id
FROM permissions
WHERE permission_name NOT IN (
    'edit_others_private_journey',
    'delete_others_private_journey',
    'view_others_private_journey',
    'edit_others_private_event',
    'delete_others_private_event',
    'view_others_private_event',
    'view_trial_page',
    'create_subscription',
    'create_trial',
    'receive_gift'
);
-- Premium permissions
INSERT INTO role_permissions (role_id, permission_id)
SELECT 4, permission_id FROM permissions WHERE is_default = TRUE
UNION
SELECT 4, permission_id FROM permissions WHERE permission_name IN (
    'publish_journey',
    'add_multiple_photos',
	'view_own_edit_log',
	'view_others_public_profile_map',
	'view_own_subscriptions',
	'view_own_payments',
	'create_journey_cover',
	'delete_journey_cover',
	'view_premium_achievements',
	'follow_journey',
	'follow_user',
	'follow_location',
    'create_subscription',
    'receive_gift',
    'use_premium_features',
    'view_departure_board',
    'view_subscription_expired_notification',
    'create_no_edits_flag',
    'view_own_no_edits_flag'
) AND is_default = FALSE;
-- Trial permissions
INSERT INTO role_permissions (role_id, permission_id)
SELECT 5, permission_id FROM permissions WHERE is_default = TRUE
UNION
SELECT 5, permission_id FROM permissions WHERE permission_name IN (
    'publish_journey',
    'add_multiple_photos',
	'view_own_edit_log',
	'view_others_public_profile_map',
	'view_own_subscriptions',
	'view_own_payments',
	'create_journey_cover',
	'delete_journey_cover',
	'view_premium_achievements',
	'follow_journey',
	'follow_user',
	'follow_location',
    'create_subscription',
    'receive_gift',
    'use_premium_features',
    'view_departure_board',
    'view_subscription_expired_notification',
    'create_no_edits_flag',
    'view_own_no_edits_flag'
) AND is_default = FALSE;
-- Support Tech permissions
INSERT INTO role_permissions (role_id, permission_id)
SELECT 6, permission_id
FROM permissions
WHERE permission_name NOT IN (
    'edit_others_private_journey',
    'delete_others_private_journey',
    'view_others_private_journey',
    'edit_others_private_event',
    'delete_others_private_event',
    'view_others_private_event',
    'update_roles',
    'view_trial_page',
    'create_subscription',
    'create_trial',
    'receive_gift'
);

-- Subscription Plans
INSERT INTO subscription_plans
(name, duration_months, discount_percent, price_excl_gst, gst_percentage, subscription_type)
VALUES
('Free Trial', 1, NULL, NULL, NULL, 'Trial'),
('One Month', 1, 0.00, 5.22, 15, 'Purchased'),
('One Quarter', 3, 10.00, 14.09, 15, 'Purchased'),
('One Year', 12, 25.00, 46.96, 15, 'Purchased'),
('Reward One Month', 1, NULL, NULL, NULL, 'Gifted'),
('Reward One Quarter', 3, NULL, NULL, NULL, 'Gifted'),
('Reward One Year', 12, NULL, NULL, NULL, 'Gifted');

-- location
 INSERT INTO locations (location_id, `name`) VALUES
 (1, 'New Zealand'),
 (2, 'London'),
 (3, 'Japan'),
 (4, 'Jamaica'),
 (5, 'Ireland'),
 (6, 'England'),
 (7, 'Ashburton'),
 (8, 'Russia'),
 (9, 'China'),
 (10, 'Guyana'),
 (11, 'Australia'),
 (12, 'Greece'),
 (13, 'Malaysia'),
 (14, 'USA'),
 (15, 'Poland'),
 (16, 'New York'),
 (17, 'Barbados'),
 (18, 'Fiji'),
 (19, 'Malta'),
 (20, 'Canada'),
 (21, 'Uruguay'),
 (22, 'Slovenia'),
 (23, 'Qatar'),
 (24, 'Scotland'),
 (25, 'Singapore');

-- Journey 1: European Adventure
INSERT INTO journeys (journey_id, user_id, title, `description`, `start_date`, create_time, update_by, update_time, `status`, `hidden`) VALUES
(1, 1, 'European Adventure', 'Exploring major cities in Europe', '2024-04-15', '2024-05-10 08:23:45', NULL, '2024-05-10 08:23:45', 'public', FALSE);
INSERT INTO events (event_id, journey_id, user_id, location_id, title, `description`, `start_date`, end_date, create_time, update_by, update_time) VALUES
(1, 1, 1, 2, 'London Arrival', 'First day in London, visiting Big Ben', '2024-06-15 10:00:00', '2024-06-15 18:00:00', '2024-05-11 09:15:00', NULL, '2024-05-11 09:15:00'),
(2, 1, 1, 6, 'British Museum', 'Exploring famous artworks', '2024-06-16 09:00:00', '2024-06-16 16:00:00', '2024-05-12 14:20:00', NULL, '2024-05-12 14:20:00'),
(3, 1, 1, 6, 'English Countryside', 'Exploring rural England', '2024-06-18 11:00:00', '2024-06-18 15:00:00', '2024-05-15 10:45:00', NULL, '2024-05-15 10:45:00'),
(4, 1, 1, 6, 'Stonehenge', 'Historical tour of ancient site', '2024-06-20 10:00:00', '2024-06-20 14:00:00', '2024-05-18 16:30:00', NULL, '2024-05-18 16:30:00'),
(5, 1, 1, 5, 'Dublin Castle', 'Exploring the castle complex', '2024-06-22 09:00:00', '2024-06-22 17:00:00', '2024-05-20 11:10:00', NULL, '2024-05-20 11:10:00');

-- Journey 2: Asian Backpacking
INSERT INTO journeys (journey_id, user_id, title, `description`, `start_date`, create_time, update_by, update_time, `status`, `hidden`) VALUES
(2, 2, 'Asian Backpacking', 'Backpacking through Southeast Asia', '2023-07-01', '2023-08-15 14:12:33', NULL, '2023-08-15 14:12:33', 'public', FALSE);
INSERT INTO events (event_id, journey_id, user_id, location_id, title, `description`, `start_date`, end_date, create_time, update_by, update_time) VALUES
(6, 2, 2, 3, 'Tokyo Arrival', 'Exploring street markets', '2023-07-01 14:00:00', '2023-07-01 20:00:00', '2023-08-16 10:20:00', NULL, '2023-08-16 10:20:00'),
(7, 2, 2, 3, 'Kyoto Temples', 'Visiting ancient temples', '2023-07-03 08:00:00', '2023-07-03 16:00:00', '2023-08-17 14:35:00', NULL, '2023-08-17 14:35:00'),
(8, 2, 2, 9, 'Great Wall', 'Hiking the Great Wall', '2023-07-06 05:00:00', '2023-07-06 09:00:00', '2023-08-18 09:50:00', NULL, '2023-08-18 09:50:00'),
(9, 2, 2, 25, 'Singapore Gardens', 'Exploring Gardens by the Bay', '2023-07-08 10:00:00', '2023-07-09 14:00:00', '2023-08-19 16:15:00', NULL, '2023-08-19 16:15:00'),
(10, 2, 2, 13, 'Kuala Lumpur Street Food', 'Exploring local night markets and trying Malaysian cuisine', '2023-07-11 18:00:00', '2023-07-11 23:00:00', '2023-08-20 12:30:00', NULL, '2023-08-20 12:30:00');

-- Journey 3: USA Road Trip
INSERT INTO journeys (journey_id, user_id, title, `description`, `start_date`, create_time, update_by, update_time, `status`, `hidden`) VALUES
(3, 3, 'USA Road Trip', 'Cross-country road trip from NY to LA', '2024-08-01', '2024-08-05 09:45:21', NULL, '2024-08-05 09:45:21', 'public', FALSE);
INSERT INTO events (event_id, journey_id, user_id, location_id, title, `description`, `start_date`, end_date, create_time, update_by, update_time) VALUES
(11, 3, 3, 16, 'NYC Departure', 'Starting the road trip from Times Square', '2024-08-10 08:00:00', '2024-08-10 10:00:00', '2024-08-05 15:30:00', NULL, '2024-08-05 15:30:00'),
(12, 3, 3, 14, 'Chicago Deep Dish', 'Trying famous Chicago pizza', '2024-08-12 18:00:00', '2024-08-12 20:00:00', '2024-08-07 11:45:00', NULL, '2024-08-07 11:45:00'),
(13, 3, 3, 14, 'Grand Canyon', 'Hiking the South Rim', '2024-08-15 09:00:00', '2024-08-15 15:00:00', '2024-08-09 14:20:00', NULL, '2024-08-09 14:20:00'),
(14, 3, 3, 14, 'Yellowstone NP', 'Exploring geysers and wildlife', '2024-08-17 07:00:00', '2024-08-19 18:00:00', '2024-08-11 10:15:00', NULL, '2024-08-11 10:15:00'),
(15, 3, 3, 14, 'San Francisco', 'Golden Gate Bridge visit', '2024-08-21 06:00:00', '2024-08-21 18:00:00', '2024-08-13 16:40:00', NULL, '2024-08-13 16:40:00');

-- Journey 4: Australian Wildlife Adventure
INSERT INTO journeys (journey_id, user_id, title, `description`, `start_date`, create_time, update_by, update_time, `status`, `hidden`) VALUES
(4, 4, 'Australian Wildlife Adventure', 'Wildlife photography and adventure across Australia', '2023-09-05', '2023-06-22 16:30:18', NULL, '2023-06-22 16:30:18', 'public', TRUE);
INSERT INTO events (event_id, journey_id, user_id, location_id, title, `description`, `start_date`, end_date, create_time, update_by, update_time) VALUES
(16, 4, 4, 11, 'Sydney Arrival', 'Preparing for outback adventure', '2023-09-05 12:00:00', '2023-09-05 18:00:00', '2023-06-23 09:30:00', NULL, '2023-06-23 09:30:00'),
(17, 4, 4, 11, 'Kangaroo Spotting', 'Wildlife viewing', '2023-09-06 05:00:00', '2023-09-06 10:00:00', '2023-06-25 14:50:00', NULL, '2023-06-25 14:50:00'),
(18, 4, 4, 11, 'Uluru Sunset', 'Viewing the color changes', '2023-09-07 06:00:00', '2023-09-07 11:00:00', '2023-06-27 11:20:00', NULL, '2023-06-27 11:20:00'),
(19, 4, 4, 11, 'Great Barrier Reef', 'Snorkeling adventure', '2023-09-09 04:00:00', '2023-09-09 08:00:00', '2023-06-29 16:10:00', NULL, '2023-06-29 16:10:00'),
(20, 4, 4, 11, 'Blue Mountains Bushwalk', 'Hiking through eucalyptus forests and spotting native wildlife', '2023-09-11 07:00:00', '2023-09-11 15:00:00', '2023-06-30 10:45:00', NULL, '2023-06-30 10:45:00');

-- Journey 5: Mediterranean Cruise
INSERT INTO journeys (journey_id, user_id, title, `description`, `start_date`, create_time, update_by, update_time, `status`, `hidden`) VALUES
(5, 5, 'Mediterranean Cruise', 'Island hopping in Greece and Italy', '2024-05-20', '2024-05-25 11:20:55', NULL, '2024-05-25 11:20:55', 'public', FALSE);
INSERT INTO events (event_id, journey_id, user_id, location_id, title, `description`, `start_date`, end_date, create_time, update_by, update_time) VALUES
(21, 5, 5, 12, 'Athens Acropolis', 'Exploring ancient ruins', '2024-05-20 08:00:00', '2024-05-20 14:00:00', '2024-05-26 10:25:00', NULL, '2024-05-26 10:25:00'),
(22, 5, 5, 12, 'Santorini Sunset', 'Oia village sunset viewing', '2024-05-22 17:00:00', '2024-05-22 20:00:00', '2024-05-27 14:40:00', NULL, '2024-05-27 14:40:00'),
(23, 5, 5, 19, 'Valletta Tour', 'Exploring Maltese capital', '2024-05-24 10:00:00', '2024-05-24 18:00:00', '2024-05-28 11:15:00', NULL, '2024-05-28 11:15:00'),
(24, 5, 5, 12, 'Mykonos Windmills', 'Traditional Greek island architecture', '2024-05-26 09:00:00', '2024-05-26 16:00:00', '2024-05-29 12:30:00', NULL, '2024-05-29 12:30:00'),
(25, 5, 5, 12, 'Crete Palace', 'Exploring Minoan ruins at Knossos', '2024-05-28 10:00:00', '2024-05-28 15:00:00', '2024-05-30 14:45:00', NULL, '2024-05-30 14:45:00');

-- Journey 6: Himalayan Trek
INSERT INTO journeys (journey_id, user_id, title, `description`, `start_date`, create_time, update_by, update_time, `status`, `hidden`) VALUES
(6, 6, 'Himalayan Trek', 'Trekking to Everest Base Camp', '2024-09-21', '2024-09-30 13:15:42', NULL, '2024-09-30 13:15:42', 'private', FALSE);
INSERT INTO events (event_id, journey_id, user_id, location_id, title, `description`, `start_date`, end_date, create_time, update_by, update_time) VALUES
(26, 6, 6, 9, 'Beijing Preparation', 'Gear check and briefing', '2024-10-01 09:00:00', '2024-10-01 14:00:00', '2024-09-30 15:30:00', NULL, '2024-09-30 15:30:00'),
(27, 6, 6, 9, 'Great Wall Hike', 'Hiking the Great Wall', '2024-10-02 06:00:00', '2024-10-02 08:00:00', '2024-10-01 10:20:00', NULL, '2024-10-01 10:20:00'),
(28, 6, 6, 9, 'Tibetan Plateau', 'High altitude acclimatization', '2024-10-04 08:00:00', '2024-10-04 16:00:00', '2024-10-03 14:45:00', NULL, '2024-10-03 14:45:00'),
(29, 6, 6, 9, 'Base Camp Approach', 'Final ascent to Everest Base Camp', '2024-10-06 05:00:00', '2024-10-06 18:00:00', '2024-10-05 09:15:00', NULL, '2024-10-05 09:15:00'),
(30, 6, 6, 9, 'Summit Return', 'Descending back to base camp', '2024-10-08 06:00:00', '2024-10-08 16:00:00', '2024-10-07 11:30:00', NULL, '2024-10-07 11:30:00');

-- Journey 7: South American Tour
INSERT INTO journeys (journey_id, user_id, title, `description`, `start_date`, create_time, update_by, update_time, `status`, `hidden`) VALUES
(7, 7, 'South American Tour', 'Visiting Machu Picchu and Amazon', '2023-11-15', '2024-01-18 10:05:37', NULL, '2024-01-18 10:05:37', 'private', FALSE);
INSERT INTO events (event_id, journey_id, user_id, location_id, title, `description`, `start_date`, end_date, create_time, update_by, update_time) VALUES
(31, 7, 7, 21, 'Montevideo Arrival', 'Exploring Uruguayan capital', '2023-11-15 04:00:00', '2023-11-15 12:00:00', '2024-01-19 09:10:00', NULL, '2024-01-19 09:10:00'),
(32, 7, 7, 21, 'Punta del Este', 'Beach relaxation', '2023-11-17 06:00:00', '2023-11-19 18:00:00', '2024-01-20 14:30:00', NULL, '2024-01-20 14:30:00'),
(33, 7, 7, 21, 'Colonia del Sacramento', 'Historic town visit', '2023-11-21 09:00:00', '2023-11-21 15:00:00', '2024-01-22 11:25:00', NULL, '2024-01-22 11:25:00'),
(34, 7, 7, 21, 'Amazon Rainforest', 'Wildlife observation in the jungle', '2023-11-23 07:00:00', '2023-11-25 17:00:00', '2024-01-23 13:40:00', NULL, '2024-01-23 13:40:00'),
(35, 7, 7, 21, 'Machu Picchu', 'Ancient Incan ruins exploration', '2023-11-27 05:00:00', '2023-11-27 14:00:00', '2024-01-24 15:55:00', NULL, '2024-01-24 15:55:00');

-- Journey 8: Antarctic Expedition
INSERT INTO journeys (journey_id, user_id, title, `description`, `start_date`, create_time, update_by, update_time, `status`, `hidden`) VALUES
(8, 8, 'Antarctic Expedition', 'Scientific research voyage', '2024-12-01', '2024-10-12 15:22:19', NULL, '2024-10-12 15:22:19', 'private', TRUE);
INSERT INTO events (event_id, journey_id, user_id, location_id, title, `description`, `start_date`, end_date, create_time, update_by, update_time) VALUES
(36, 8, 8, 21, 'Montevideo Departure', 'Boarding the expedition ship', '2024-12-01 16:00:00', '2024-12-01 18:00:00', '2024-10-13 10:45:00', NULL, '2024-10-13 10:45:00'),
(37, 8, 8, 20, 'Canadian Arctic', 'Exploring northern waters', '2024-12-03 06:00:00', '2024-12-05 18:00:00', '2024-10-15 14:20:00', NULL, '2024-10-15 14:20:00'),
(38, 8, 8, 20, 'Iceberg Viewing', 'First iceberg sightings', '2024-12-07 08:00:00', '2024-12-07 16:00:00', '2024-10-17 16:50:00', NULL, '2024-10-17 16:50:00'),
(39, 8, 8, 20, 'Polar Wildlife', 'Penguin and seal observation', '2024-12-09 05:00:00', '2024-12-09 19:00:00', '2024-10-19 12:25:00', NULL, '2024-10-19 12:25:00'),
(40, 8, 8, 20, 'Research Station', 'Scientific data collection', '2024-12-11 09:00:00', '2024-12-11 17:00:00', '2024-10-21 14:40:00', NULL, '2024-10-21 14:40:00');

-- Journey 9: Middle East Discovery
INSERT INTO journeys (journey_id, user_id, title, `description`, `start_date`, create_time, update_by, update_time, `status`, `hidden`) VALUES
(9, 9, 'Middle East Discovery', 'Exploring ancient historical sites', '2024-12-10', '2024-12-28 12:18:26', NULL, '2024-12-28 12:18:26', 'private', FALSE);
INSERT INTO events (event_id, journey_id, user_id, location_id, title, `description`, `start_date`, end_date, create_time, update_by, update_time) VALUES
(41, 9, 9, 23, 'Doha Arrival', 'Exploring Qatari capital', '2025-01-10 07:00:00', '2025-01-10 17:00:00', '2024-12-29 09:30:00', NULL, '2024-12-29 09:30:00'),
(42, 9, 9, 23, 'Desert Safari', 'Dune bashing adventure', '2025-01-12 14:00:00', '2025-01-13 10:00:00', '2024-12-30 14:15:00', NULL, '2024-12-30 14:15:00'),
(43, 9, 9, 23, 'Souq Waqif', 'Traditional market exploration', '2025-01-15 09:00:00', '2025-01-15 15:00:00', '2025-01-02 11:40:00', NULL, '2025-01-02 11:40:00'),
(44, 9, 9, 23, 'Museum of Islamic Art', 'Cultural heritage exploration', '2025-01-17 10:00:00', '2025-01-17 16:00:00', '2025-01-03 13:20:00', NULL, '2025-01-03 13:20:00'),
(45, 9, 9, 23, 'Pearl Diving Experience', 'Traditional Qatar pearl diving', '2025-01-19 08:00:00', '2025-01-19 14:00:00', '2025-01-04 15:35:00', NULL, '2025-01-04 15:35:00');

-- Journey 10: Australian Outback
INSERT INTO journeys (journey_id, user_id, title, `description`, `start_date`, create_time, update_by, update_time, `status`, `hidden`) VALUES
(10, 10, 'Australian Outback', 'Camping in the Australian wilderness', '2023-02-20', '2025-01-25 09:40:13', NULL, '2025-01-25 09:40:13', 'private', FALSE);
INSERT INTO events (event_id, journey_id, user_id, location_id, title, `description`, `start_date`, end_date, create_time, update_by, update_time) VALUES
(46, 10, 10, 11, 'Sydney Arrival', 'Opera House visit', '2023-02-20 17:00:00', '2023-02-20 19:00:00', '2025-01-26 10:20:00', NULL, '2025-01-26 10:20:00'),
(47, 10, 10, 11, 'Great Ocean Road', 'Scenic coastal drive', '2023-02-22 06:00:00', '2023-02-22 14:00:00', '2025-01-27 14:35:00', NULL, '2025-01-27 14:35:00'),
(48, 10, 10, 11, 'Melbourne', 'Cultural center visit', '2023-02-24 09:00:00', '2023-02-24 15:00:00', '2025-01-28 11:50:00', NULL, '2025-01-28 11:50:00'),
(49, 10, 10, 11, 'Ayers Rock', 'Sacred Aboriginal site', '2023-02-26 05:00:00', '2023-02-26 18:00:00', '2025-01-29 16:15:00', NULL, '2025-01-29 16:15:00'),
(50, 10, 10, 11, 'Outback Camping', 'Night under the stars', '2023-02-28 19:00:00', '2023-03-01 07:00:00', '2025-01-30 18:40:00', NULL, '2025-01-30 18:40:00');

-- Journey 11: Nordic Lights Tour
INSERT INTO journeys (journey_id, user_id, title, `description`, `start_date`, create_time, update_by, update_time, `status`, `hidden`) VALUES
(11, 11, 'Nordic Lights Tour', 'Chasing Northern Lights in Scandinavia', '2024-11-15', '2024-11-17 14:55:48', NULL, '2024-11-17 14:55:48', 'public', FALSE);
INSERT INTO events (event_id, journey_id, user_id, location_id, title, `description`, `start_date`, end_date, create_time, update_by, update_time) VALUES
(51, 11, 11, 22, 'Ljubljana Arrival', 'Exploring Slovenian capital', '2024-11-15 12:00:00', '2024-11-15 18:00:00', '2024-11-18 09:15:00', NULL, '2024-11-18 09:15:00'),
(52, 11, 11, 22, 'Lake Bled', 'Exploring alpine lake', '2024-11-16 10:00:00', '2024-11-16 14:00:00', '2024-11-19 14:30:00', NULL, '2024-11-19 14:30:00'),
(53, 11, 11, 22, 'Postojna Cave', 'Underground cave system', '2024-11-17 20:00:00', '2024-11-17 23:00:00', '2024-11-20 16:45:00', NULL, '2024-11-20 16:45:00'),
(54, 11, 11, 22, 'Aurora Hunting', 'Northern lights photography', '2024-11-18 22:00:00', '2024-11-19 03:00:00', '2024-11-21 11:20:00', NULL, '2024-11-21 11:20:00'),
(55, 11, 11, 22, 'Mountain Hiking', 'Alpine trail exploration', '2024-11-19 08:00:00', '2024-11-19 16:00:00', '2024-11-22 13:55:00', NULL, '2024-11-22 13:55:00');

-- Journey 12: Japanese Cultural Journey
INSERT INTO journeys (journey_id, user_id, title, `description`, `start_date`, create_time, update_by, update_time, `status`, `hidden`) VALUES
(12, 12, 'Japanese Cultural Journey', 'Temples and tea ceremonies', '2024-04-01', '2024-04-15 08:30:22', NULL, '2024-04-15 08:30:22', 'public', FALSE);
INSERT INTO events (event_id, journey_id, user_id, location_id, title, `description`, `start_date`, end_date, create_time, update_by, update_time) VALUES
(56, 12, 12, 3, 'Tokyo Arrival', 'Exploring Shibuya crossing', '2024-04-01 14:00:00', '2024-04-01 20:00:00', '2024-04-16 10:20:00', NULL, '2024-04-16 10:20:00'),
(57, 12, 12, 3, 'Kyoto Temples', 'Golden Pavilion visit', '2024-04-03 09:00:00', '2024-04-03 16:00:00', '2024-04-17 14:35:00', NULL, '2024-04-17 14:35:00'),
(58, 12, 12, 3, 'Tea Ceremony', 'Traditional Japanese tea experience', '2024-04-05 11:00:00', '2024-04-05 13:00:00', '2024-04-18 11:50:00', NULL, '2024-04-18 11:50:00'),
(59, 12, 12, 3, 'Mount Fuji', 'Sacred mountain pilgrimage', '2024-04-07 06:00:00', '2024-04-07 18:00:00', '2024-04-19 16:25:00', NULL, '2024-04-19 16:25:00'),
(60, 12, 12, 3, 'Zen Garden', 'Meditation and reflection', '2024-04-09 09:00:00', '2024-04-09 15:00:00', '2024-04-20 12:40:00', NULL, '2024-04-20 12:40:00');

-- Journey 13: Trans-Siberian Railway
INSERT INTO journeys (journey_id, user_id, title, `description`, `start_date`, create_time, update_by, update_time, `status`, `hidden`) VALUES
(13, 13, 'Trans-Siberian Railway', 'Moscow to Vladivostok by train', '2024-05-01', '2024-05-01 17:12:39', NULL, '2024-05-01 17:12:39', 'public', TRUE);
INSERT INTO events (event_id, journey_id, user_id, location_id, title, `description`, `start_date`, end_date, create_time, update_by, update_time) VALUES
(61, 13, 13, 8, 'Moscow Departure', 'Boarding the train at Yaroslavsky', '2024-05-01 12:00:00', '2024-05-01 13:00:00', '2024-05-02 09:30:00', NULL, '2024-05-02 09:30:00'),
(62, 13, 13, 8, 'Yekaterinburg', 'Stopover and city tour', '2024-05-03 08:00:00', '2024-05-03 18:00:00', '2024-05-03 14:15:00', NULL, '2024-05-03 14:15:00'),
(63, 13, 13, 8, 'Lake Baikal', 'Scenic views of the lake', '2024-05-05 06:00:00', '2024-05-05 20:00:00', '2024-05-05 11:40:00', NULL, '2024-05-05 11:40:00'),
(64, 13, 13, 8, 'Siberian Taiga', 'Forest wilderness experience', '2024-05-07 10:00:00', '2024-05-07 16:00:00', '2024-05-07 13:20:00', NULL, '2024-05-07 13:20:00'),
(65, 13, 13, 8, 'Vladivostok Arrival', 'Pacific coast destination', '2024-05-09 15:00:00', '2024-05-09 19:00:00', '2024-05-09 17:45:00', NULL, '2024-05-09 17:45:00');

-- Journey 14: Caribbean Vacation
INSERT INTO journeys (journey_id, user_id, title, `description`, `start_date`, create_time, update_by, update_time, `status`, `hidden`) VALUES
(14, 14, 'Caribbean Vacation', 'Relaxing on tropical islands', '2024-06-05', '2024-06-05 10:25:16', NULL, '2024-06-05 10:25:16', 'public', FALSE);
INSERT INTO events (event_id, journey_id, user_id, location_id, title, `description`, `start_date`, end_date, create_time, update_by, update_time) VALUES
(66, 14, 14, 4, 'Montego Bay Arrival', 'Beach resort check-in', '2024-06-05 15:00:00', '2024-06-05 17:00:00', '2024-06-05 12:30:00', NULL, '2024-06-05 12:30:00'),
(67, 14, 14, 4, 'Dunn River Falls', 'Climbing the waterfalls', '2024-06-06 09:00:00', '2024-06-06 12:00:00', '2024-06-06 10:45:00', NULL, '2024-06-06 10:45:00'),
(68, 14, 14, 17, 'Barbados Tour', 'Island exploration', '2024-06-07 10:00:00', '2024-06-07 14:00:00', '2024-06-07 14:20:00', NULL, '2024-06-07 14:20:00'),
(69, 14, 14, 18, 'Fiji Paradise', 'Crystal clear waters and coral reefs', '2024-06-08 08:00:00', '2024-06-08 17:00:00', '2024-06-08 11:15:00', NULL, '2024-06-08 11:15:00'),
(70, 14, 14, 4, 'Reggae Festival', 'Local music and culture', '2024-06-09 18:00:00', '2024-06-09 23:00:00', '2024-06-09 16:30:00', NULL, '2024-06-09 16:30:00');

-- Journey 15: Alaskan Wilderness
INSERT INTO journeys (journey_id, user_id, title, `description`, `start_date`, create_time, update_by, update_time, `status`, `hidden`) VALUES
(15, 15, 'Alaskan Wilderness', 'Dog sledding and glacier tours', '2024-07-20', '2024-07-20 13:45:27', NULL, '2024-07-20 13:45:27', 'public', FALSE);
INSERT INTO events (event_id, journey_id, user_id, location_id, title, `description`, `start_date`, end_date, create_time, update_by, update_time) VALUES
(71, 15, 15, 14, 'Anchorage Arrival', 'Gear preparation', '2024-07-20 10:00:00', '2024-07-20 14:00:00', '2024-07-20 15:30:00', NULL, '2024-07-20 15:30:00'),
(72, 15, 15, 14, 'Denali NP', 'Wildlife viewing', '2024-07-22 06:00:00', '2024-07-24 18:00:00', '2024-07-21 10:20:00', NULL, '2024-07-21 10:20:00'),
(73, 15, 15, 20, 'Canadian Rockies', 'Mountain exploration', '2024-07-26 08:00:00', '2024-07-26 16:00:00', '2024-07-23 14:45:00', NULL, '2024-07-23 14:45:00'),
(74, 15, 15, 14, 'Glacier Bay', 'Ice formation observation', '2024-07-28 07:00:00', '2024-07-28 15:00:00', '2024-07-25 12:20:00', NULL, '2024-07-25 12:20:00'),
(75, 15, 15, 14, 'Dog Sledding', 'Traditional Alaskan transport', '2024-07-30 09:00:00', '2024-07-30 14:00:00', '2024-07-27 16:35:00', NULL, '2024-07-27 16:35:00');

-- Journey 16: Middle Earth Tour
INSERT INTO journeys (journey_id, user_id, title, `description`, `start_date`, create_time, update_by, update_time, `status`, `hidden`) VALUES
(16, 16, 'Middle Earth Tour', 'Lord of the Rings locations in NZ', '2023-06-15', '2022-07-19 11:10:34', NULL, '2022-07-19 11:10:34', 'public', FALSE);
INSERT INTO events (event_id, journey_id, user_id, location_id, title, `description`, `start_date`, end_date, create_time, update_by, update_time) VALUES
(76, 16, 16, 1, 'Auckland Arrival', 'Exploring New Zealand', '2023-06-15 09:00:00', '2023-06-15 14:00:00', '2022-07-20 11:15:00', NULL, '2022-07-20 11:15:00'),
(77, 16, 16, 1, 'Hobbiton', 'Visiting the movie set', '2023-06-17 10:00:00', '2023-06-17 16:00:00', '2022-07-22 14:30:00', NULL, '2022-07-22 14:30:00'),
(78, 16, 16, 1, 'Rotorua', 'Geothermal wonders', '2023-06-19 06:00:00', '2023-06-19 18:00:00', '2022-07-24 16:45:00', NULL, '2022-07-24 16:45:00'),
(79, 16, 16, 1, 'Mount Doom', 'Tongariro National Park', '2023-06-21 05:00:00', '2023-06-21 17:00:00', '2022-07-26 09:40:00', NULL, '2022-07-26 09:40:00'),
(80, 16, 16, 1, 'Queenstown Adventure', 'Adventure sports capital', '2023-06-23 08:00:00', '2023-06-23 19:00:00', '2022-07-28 13:25:00', NULL, '2022-07-28 13:25:00');

-- Journey 17: Silicon Valley Tech Tour
INSERT INTO journeys (journey_id, user_id, title, `description`, `start_date`, create_time, update_by, update_time, `status`, `hidden`) VALUES
(17, 17, 'Silicon Valley Tech Tour', 'Visiting major tech company HQs', '2024-07-01', '2024-08-07 15:33:41', NULL, '2024-08-07 15:33:41', 'public', TRUE);
INSERT INTO events (event_id, journey_id, user_id, location_id, title, `description`, `start_date`, end_date, create_time, update_by, update_time) VALUES
(81, 17, 17, 14, 'San Francisco Arrival', 'Tech company tours', '2024-07-01 10:00:00', '2024-07-01 12:00:00', '2024-08-08 09:30:00', NULL, '2024-08-08 09:30:00'),
(82, 17, 17, 14, 'Googleplex', 'Exploring the campus', '2024-07-02 13:00:00', '2024-07-02 15:00:00', '2024-08-09 14:15:00', NULL, '2024-08-09 14:15:00'),
(83, 17, 17, 14, 'Computer History Museum', 'Learning about tech evolution', '2024-07-03 09:00:00', '2024-07-03 14:00:00', '2024-08-10 11:40:00', NULL, '2024-08-10 11:40:00'),
(84, 17, 17, 14, 'Apple Park', 'Visiting the Apple headquarters', '2024-07-04 11:00:00', '2024-07-04 15:00:00', '2024-08-11 16:20:00', NULL, '2024-08-11 16:20:00'),
(85, 17, 17, 14, 'Stanford University', 'Innovation and research hub', '2024-07-05 14:00:00', '2024-07-05 17:00:00', '2024-08-12 12:45:00', NULL, '2024-08-12 12:45:00');

-- Journey 18: Wine Country Exploration
INSERT INTO journeys (journey_id, user_id, title, `description`, `start_date`, create_time, update_by, update_time, `status`, `hidden`) VALUES
(18, 18, 'Wine Country Exploration', 'Vineyard tours in France and Italy', '2024-10-10', '2024-10-11 09:20:58', NULL, '2024-10-11 09:20:58', 'public', FALSE);
INSERT INTO events (event_id, journey_id, user_id, location_id, title, `description`, `start_date`, end_date, create_time, update_by, update_time) VALUES
(86, 18, 18, 6, 'English Vineyards', 'Wine tasting tour', '2024-10-10 10:00:00', '2024-10-10 16:00:00', '2024-10-12 10:20:00', NULL, '2024-10-12 10:20:00'),
(87, 18, 18, 5, 'Irish Whiskey', 'Distillery tour', '2024-10-12 09:00:00', '2024-10-12 17:00:00', '2024-10-13 14:35:00', NULL, '2024-10-13 14:35:00'),
(88, 18, 18, 2, 'London Gin', 'Tasting experience', '2024-10-14 11:00:00', '2024-10-14 15:00:00', '2024-10-15 11:50:00', NULL, '2024-10-15 11:50:00'),
(89, 18, 18, 6, 'Cotswolds Brewery', 'Traditional English brewing', '2024-10-16 10:00:00', '2024-10-16 16:00:00', '2024-10-17 13:30:00', NULL, '2024-10-17 13:30:00'),
(90, 18, 18, 24, 'Scottish Highlands', 'Single malt whisky trail', '2024-10-18 09:00:00', '2024-10-18 18:00:00', '2024-10-19 15:15:00', NULL, '2024-10-19 15:15:00');

-- Journey 19: Arctic Circle Adventure
INSERT INTO journeys (journey_id, user_id, title, `description`, `start_date`, create_time, update_by, update_time, `status`, `hidden`) VALUES
(19, 19, 'Arctic Circle Adventure', 'Exploring northernmost settlements', '2024-10-05', '2024-10-11 14:05:12', NULL, '2024-10-11 14:05:12', 'public', FALSE);
INSERT INTO events (event_id, journey_id, user_id, location_id, title, `description`, `start_date`, end_date, create_time, update_by, update_time) VALUES
(91, 19, 19, 20, 'Yellowknife Arrival', 'Northern lights viewing', '2024-10-05 12:00:00', '2024-10-05 16:00:00', '2024-10-12 09:30:00', NULL, '2024-10-12 09:30:00'),
(92, 19, 19, 20, 'Dog Sledding', 'Mushing through snow', '2024-10-07 09:00:00', '2024-10-07 14:00:00', '2024-10-14 14:15:00', NULL, '2024-10-14 14:15:00'),
(93, 19, 19, 20, 'Ice Road', 'Frozen lake exploration', '2024-10-09 10:00:00', '2024-10-09 16:00:00', '2024-10-16 11:40:00', NULL, '2024-10-16 11:40:00'),
(94, 19, 19, 20, 'Inuit Village', 'Traditional Arctic culture', '2024-10-11 11:00:00', '2024-10-11 17:00:00', '2024-10-18 16:25:00', NULL, '2024-10-18 16:25:00'),
(95, 19, 19, 20, 'Polar Bears', 'Wildlife observation expedition', '2024-10-13 06:00:00', '2024-10-13 18:00:00', '2024-10-20 14:50:00', NULL, '2024-10-20 14:50:00');

-- Journey 20: World War History Tour
INSERT INTO journeys (journey_id, user_id, title, `description`, `start_date`, create_time, update_by, update_time, `status`, `hidden`) VALUES
(20, 20, 'World War History Tour', 'Visiting important battle sites', '2024-12-20', '2025-01-28 16:50:29', NULL, '2025-01-28 16:50:29', 'public', FALSE);
INSERT INTO events (event_id, journey_id, user_id, location_id, title, `description`, `start_date`, end_date, create_time, update_by, update_time) VALUES
(96, 20, 20, 6, 'London War Rooms', 'Churchill War Rooms visit', '2024-12-20 09:00:00', '2024-12-20 17:00:00', '2025-01-29 10:20:00', NULL, '2025-01-29 10:20:00'),
(97, 20, 20, 15, 'Auschwitz', 'Concentration camp memorial', '2024-12-22 08:00:00', '2024-12-22 16:00:00', '2025-01-30 14:35:00', NULL, '2025-01-30 14:35:00'),
(98, 20, 20, 6, 'Imperial War Museum', 'Military history exploration', '2024-12-24 10:00:00', '2024-12-24 15:00:00', '2025-01-31 11:50:00', NULL, '2025-01-31 11:50:00'),
(99, 20, 20, 15, 'Warsaw Ghetto', 'Holocaust remembrance site', '2024-12-26 09:00:00', '2024-12-26 16:00:00', '2025-02-01 13:40:00', NULL, '2025-02-01 13:40:00'),
(100, 20, 20, 6, 'Normandy Beaches', 'D-Day landing sites', '2024-12-28 08:00:00', '2024-12-28 17:00:00', '2025-02-02 15:25:00', NULL, '2025-02-02 15:25:00');

-- Additional Private and Public Journeys for Users 11-20

-- User 11 (Benjamin Brooks) - Private Journey
INSERT INTO journeys (journey_id, user_id, title, `description`, `start_date`, create_time, update_by, update_time, `status`, `hidden`) VALUES
(21, 11, 'Secret Alpine Retreat', 'Personal mountain escape and photography', '2024-03-15', '2024-03-20 10:30:00', NULL, '2024-03-20 10:30:00', 'private', FALSE);

INSERT INTO events (event_id, journey_id, user_id, location_id, title, `description`, `start_date`, end_date, create_time, update_by, update_time) VALUES
(101, 21, 11, 22, 'Mountain Cabin Arrival', 'Secluded cabin check-in for personal retreat', '2024-03-15 14:00:00', '2024-03-15 18:00:00', '2024-03-20 11:00:00', NULL, '2024-03-20 11:00:00'),
(102, 21, 11, 22, 'Solo Hiking Trail', 'Peaceful mountain trail exploration', '2024-03-16 08:00:00', '2024-03-16 16:00:00', '2024-03-20 12:30:00', NULL, '2024-03-20 12:30:00'),
(103, 21, 11, 22, 'Alpine Lake Photography', 'Private photography session at pristine lake', '2024-03-17 06:00:00', '2024-03-17 12:00:00', '2024-03-20 14:15:00', NULL, '2024-03-20 14:15:00'),
(104, 21, 11, 22, 'Stargazing Session', 'Night sky observation and reflection', '2024-03-18 21:00:00', '2024-03-19 02:00:00', '2024-03-20 16:45:00', NULL, '2024-03-20 16:45:00'),
(105, 21, 11, 22, 'Mountain Sunrise', 'Early morning summit for sunrise viewing', '2024-03-19 05:00:00', '2024-03-19 09:00:00', '2024-03-20 18:20:00', NULL, '2024-03-20 18:20:00');

-- User 11 (Benjamin Brooks) - Published Journey
INSERT INTO journeys (journey_id, user_id, title, `description`, `start_date`, create_time, update_by, update_time, `status`, `hidden`, cover_image) VALUES
(22, 11, 'Balkans Adventure', 'Exploring the cultural diversity of the Balkans', '2024-06-01', '2024-06-05 09:15:00', NULL, '2024-06-05 09:15:00', 'published', FALSE, 'uploads/journey/ljubljana_castle_view.jpg');
INSERT INTO events (event_id, journey_id, user_id, location_id, title, `description`, `start_date`, end_date, create_time, update_by, update_time) VALUES
(106, 22, 11, 22, 'Ljubljana City Tour', 'Exploring the charming Slovenian capital', '2024-06-01 10:00:00', '2024-06-01 18:00:00', '2024-06-05 10:30:00', NULL, '2024-06-05 10:30:00'),
(107, 22, 11, 22, 'Predjama Castle', 'Visiting the dramatic cliffside castle', '2024-06-02 09:00:00', '2024-06-02 15:00:00', '2024-06-05 12:00:00', NULL, '2024-06-05 12:00:00'),
(108, 22, 11, 22, 'Vipava Valley Wine', 'Wine tasting in beautiful valley', '2024-06-03 11:00:00', '2024-06-03 17:00:00', '2024-06-05 14:20:00', NULL, '2024-06-05 14:20:00'),
(109, 22, 11, 22, 'Triglav National Park', 'Hiking in Slovenia only national park', '2024-06-04 07:00:00', '2024-06-04 19:00:00', '2024-06-05 16:45:00', NULL, '2024-06-05 16:45:00'),
(110, 22, 11, 22, 'Coastal Piran', 'Exploring the Venetian-influenced coastal town', '2024-06-05 08:00:00', '2024-06-05 16:00:00', '2024-06-05 18:30:00', NULL, '2024-06-05 18:30:00');

-- User 12 (Harper Gray) - Private Journey
INSERT INTO journeys (journey_id, user_id, title, `description`, `start_date`, create_time, update_by, update_time, `status`, `hidden`) VALUES
(23, 12, 'Personal Wellness Journey', 'Private meditation and spa retreat', '2024-08-10', '2024-08-15 14:20:00', NULL, '2024-08-15 14:20:00', 'private', FALSE);

INSERT INTO events (event_id, journey_id, user_id, location_id, title, `description`, `start_date`, end_date, create_time, update_by, update_time) VALUES
(111, 23, 12, 3, 'Ryokan Check-in', 'Traditional Japanese inn arrival', '2024-08-10 15:00:00', '2024-08-10 18:00:00', '2024-08-15 15:00:00', NULL, '2024-08-15 15:00:00'),
(112, 23, 12, 3, 'Private Onsen Session', 'Relaxing hot spring bath', '2024-08-11 07:00:00', '2024-08-11 09:00:00', '2024-08-15 16:30:00', NULL, '2024-08-15 16:30:00'),
(113, 23, 12, 3, 'Meditation Garden', 'Peaceful garden meditation practice', '2024-08-12 06:00:00', '2024-08-12 08:00:00', '2024-08-15 18:00:00', NULL, '2024-08-15 18:00:00'),
(114, 23, 12, 3, 'Traditional Massage', 'Shiatsu massage therapy session', '2024-08-13 14:00:00', '2024-08-13 16:00:00', '2024-08-15 19:30:00', NULL, '2024-08-15 19:30:00'),
(115, 23, 12, 3, 'Forest Bathing', 'Shinrin-yoku in bamboo forest', '2024-08-14 09:00:00', '2024-08-14 15:00:00', '2024-08-15 21:00:00', NULL, '2024-08-15 21:00:00');

-- User 12 (Harper Gray) - Published Journey
INSERT INTO journeys (journey_id, user_id, title, `description`, `start_date`, create_time, update_by, update_time, `status`, `hidden`, cover_image) VALUES
(24, 12, 'Sakura Season Spectacular', 'Cherry blossom viewing across Japan', '2024-04-05', '2024-04-10 11:45:00', NULL, '2024-04-10 11:45:00', 'published', FALSE, 'uploads/events/ueno_park_hanami.jpg');

INSERT INTO events (event_id, journey_id, user_id, location_id, title, `description`, `start_date`, end_date, create_time, update_by, update_time) VALUES
(116, 24, 12, 3, 'Ueno Park Hanami', 'Cherry blossom picnic in Tokyo', '2024-04-05 10:00:00', '2024-04-05 16:00:00', '2024-04-10 12:30:00', NULL, '2024-04-10 12:30:00'),
(117, 24, 12, 3, 'Yoshino Mountain', 'Thousands of cherry trees on mountain slopes', '2024-04-07 08:00:00', '2024-04-07 18:00:00', '2024-04-10 14:15:00', NULL, '2024-04-10 14:15:00'),
(118, 24, 12, 3, 'Philosopher\'s Path', 'Kyoto\'s famous cherry-lined walking path', '2024-04-09 09:00:00', '2024-04-09 15:00:00', '2024-04-10 16:00:00', NULL, '2024-04-10 16:00:00'),
(119, 24, 12, 3, 'Matsumoto Castle', 'Black castle surrounded by pink blossoms', '2024-04-11 10:00:00', '2024-04-11 16:00:00', '2024-04-10 17:45:00', NULL, '2024-04-10 17:45:00'),
(120, 24, 12, 3, 'Night Illumination', 'Evening cherry blossom light-up ceremony', '2024-04-13 18:00:00', '2024-04-13 22:00:00', '2024-04-10 19:30:00', NULL, '2024-04-10 19:30:00');

-- User 13 (Daniel Reed) - Private Journey
INSERT INTO journeys (journey_id, user_id, title, `description`, `start_date`, create_time, update_by, update_time, `status`, `hidden`) VALUES
(25, 13, 'Solo Siberian Expedition', 'Personal wilderness survival challenge', '2024-09-01', '2024-09-05 13:30:00', NULL, '2024-09-05 13:30:00', 'private', FALSE);

INSERT INTO events (event_id, journey_id, user_id, location_id, title, `description`, `start_date`, end_date, create_time, update_by, update_time) VALUES
(121, 25, 13, 8, 'Remote Cabin Setup', 'Establishing base camp in Siberian wilderness', '2024-09-01 12:00:00', '2024-09-01 18:00:00', '2024-09-05 14:00:00', NULL, '2024-09-05 14:00:00'),
(122, 25, 13, 8, 'Ice Fishing', 'Traditional Siberian ice fishing techniques', '2024-09-02 06:00:00', '2024-09-02 14:00:00', '2024-09-05 15:30:00', NULL, '2024-09-05 15:30:00'),
(123, 25, 13, 8, 'Taiga Forest Trek', 'Deep forest exploration and foraging', '2024-09-03 08:00:00', '2024-09-03 17:00:00', '2024-09-05 17:00:00', NULL, '2024-09-05 17:00:00'),
(124, 25, 13, 8, 'Aurora Photography', 'Northern lights photography session', '2024-09-04 23:00:00', '2024-09-05 04:00:00', '2024-09-05 18:45:00', NULL, '2024-09-05 18:45:00'),
(125, 25, 13, 8, 'Wilderness Reflection', 'Final day of solitude and contemplation', '2024-09-05 09:00:00', '2024-09-05 15:00:00', '2024-09-05 20:15:00', NULL, '2024-09-05 20:15:00');

-- User 13 (Daniel Reed) - Published Journey
INSERT INTO journeys (journey_id, user_id, title, `description`, `start_date`, create_time, update_by, update_time, `status`, `hidden`, cover_image) VALUES
(26, 13, 'Eastern European Heritage', 'Exploring Slavic culture and history', '2024-07-20', '2024-07-25 16:00:00', NULL, '2024-07-25 16:00:00', 'published', FALSE, 'uploads/events/moscow_red_square.jpg');

INSERT INTO events (event_id, journey_id, user_id, location_id, title, `description`, `start_date`, end_date, create_time, update_by, update_time) VALUES
(126, 26, 13, 8, 'Moscow Red Square', 'Iconic Red Square and Kremlin tour', '2024-07-20 10:00:00', '2024-07-20 16:00:00', '2024-07-25 16:30:00', NULL, '2024-07-25 16:30:00'),
(127, 26, 13, 8, 'St. Petersburg Palaces', 'Hermitage and Winter Palace exploration', '2024-07-22 09:00:00', '2024-07-22 18:00:00', '2024-07-25 18:00:00', NULL, '2024-07-25 18:00:00'),
(128, 26, 13, 15, 'Krakow Old Town', 'Medieval Polish city center', '2024-07-24 11:00:00', '2024-07-24 17:00:00', '2024-07-25 19:30:00', NULL, '2024-07-25 19:30:00'),
(129, 26, 13, 15, 'Salt Mine Adventure', 'Underground Wieliczka Salt Mine', '2024-07-26 08:00:00', '2024-07-26 14:00:00', '2024-07-25 21:00:00', NULL, '2024-07-25 21:00:00'),
(130, 26, 13, 8, 'Golden Ring Villages', 'Traditional Russian countryside', '2024-07-28 07:00:00', '2024-07-28 19:00:00', '2024-07-25 22:30:00', NULL, '2024-07-25 22:30:00');

-- User 14 (Evelyn Price) - Private Journey
INSERT INTO journeys (journey_id, user_id, title, `description`, `start_date`, create_time, update_by, update_time, `status`, `hidden`) VALUES
(27, 14, 'Family Reunion Planning', 'Private family gathering preparation', '2024-12-15', '2024-12-20 09:45:00', NULL, '2024-12-20 09:45:00', 'private', FALSE);

INSERT INTO events (event_id, journey_id, user_id, location_id, title, `description`, `start_date`, end_date, create_time, update_by, update_time) VALUES
(131, 27, 14, 4, 'Venue Scouting', 'Finding the perfect reunion location', '2024-12-15 10:00:00', '2024-12-15 16:00:00', '2024-12-20 10:15:00', NULL, '2024-12-20 10:15:00'),
(132, 27, 14, 4, 'Catering Arrangements', 'Traditional Jamaican menu planning', '2024-12-16 14:00:00', '2024-12-16 18:00:00', '2024-12-20 11:45:00', NULL, '2024-12-20 11:45:00'),
(133, 27, 14, 4, 'Accommodation Booking', 'Family lodging arrangements', '2024-12-17 09:00:00', '2024-12-17 15:00:00', '2024-12-20 13:30:00', NULL, '2024-12-20 13:30:00'),
(134, 27, 14, 4, 'Activity Planning', 'Organizing family activities and games', '2024-12-18 11:00:00', '2024-12-18 17:00:00', '2024-12-20 15:00:00', NULL, '2024-12-20 15:00:00'),
(135, 27, 14, 4, 'Final Preparations', 'Last-minute details and confirmations', '2024-12-19 08:00:00', '2024-12-19 20:00:00', '2024-12-20 16:45:00', NULL, '2024-12-20 16:45:00');

-- User 14 (Evelyn Price) - Published Journey
INSERT INTO journeys (journey_id, user_id, title, `description`, `start_date`, create_time, update_by, update_time, `status`, `hidden`, cover_image) VALUES
(28, 14, 'Island Hopping Paradise', 'Caribbean islands exploration adventure', '2024-03-01', '2024-03-05 12:30:00', NULL, '2024-03-05 12:30:00', 'published', FALSE, 'uploads/events/barbados_beach_day.jpg');

INSERT INTO events (event_id, journey_id, user_id, location_id, title, `description`, `start_date`, end_date, create_time, update_by, update_time) VALUES
(136, 28, 14, 17, 'Barbados Beach Day', 'Crystal clear waters and white sand', '2024-03-01 09:00:00', '2024-03-01 18:00:00', '2024-03-05 13:00:00', NULL, '2024-03-05 13:00:00'),
(137, 28, 14, 4, 'Blue Mountain Coffee', 'Jamaica famous coffee plantation tour', '2024-03-03 08:00:00', '2024-03-03 16:00:00', '2024-03-05 14:30:00', NULL, '2024-03-05 14:30:00'),
(138, 28, 14, 18, 'Fiji Coral Diving', 'Underwater coral reef exploration', '2024-03-05 07:00:00', '2024-03-05 15:00:00', '2024-03-05 16:00:00', NULL, '2024-03-05 16:00:00'),
(139, 28, 14, 17, 'Rum Distillery Tour', 'Traditional Caribbean rum making', '2024-03-07 10:00:00', '2024-03-07 16:00:00', '2024-03-05 17:30:00', NULL, '2024-03-05 17:30:00'),
(140, 28, 14, 4, 'Reggae Music Festival', 'Authentic Jamaican music celebration', '2024-03-09 19:00:00', '2024-03-10 02:00:00', '2024-03-05 19:00:00', NULL, '2024-03-05 19:00:00');

-- User 15 (Matthew Cox) - Private Journey
INSERT INTO journeys (journey_id, user_id, title, `description`, `start_date`, create_time, update_by, update_time, `status`, `hidden`) VALUES
(29, 15, 'Personal Photography Project', 'Solo wilderness photography expedition', '2024-10-01', '2024-10-05 14:15:00', NULL, '2024-10-05 14:15:00', 'private', FALSE);

INSERT INTO events (event_id, journey_id, user_id, location_id, title, `description`, `start_date`, end_date, create_time, update_by, update_time) VALUES
(141, 29, 15, 14, 'Equipment Preparation', 'Camera gear setup and location scouting', '2024-10-01 08:00:00', '2024-10-01 16:00:00', '2024-10-05 14:45:00', NULL, '2024-10-05 14:45:00'),
(142, 29, 15, 14, 'Golden Hour Shoot', 'Dawn landscape photography session', '2024-10-02 05:00:00', '2024-10-02 09:00:00', '2024-10-05 16:15:00', NULL, '2024-10-05 16:15:00'),
(143, 29, 15, 14, 'Wildlife Tracking', 'Patient wildlife photography', '2024-10-03 06:00:00', '2024-10-03 18:00:00', '2024-10-05 17:45:00', NULL, '2024-10-05 17:45:00'),
(144, 29, 15, 14, 'Night Sky Session', 'Astrophotography and star trails', '2024-10-04 20:00:00', '2024-10-05 04:00:00', '2024-10-05 19:30:00', NULL, '2024-10-05 19:30:00'),
(145, 29, 15, 14, 'Portfolio Review', 'Selecting and editing best shots', '2024-10-05 10:00:00', '2024-10-05 16:00:00', '2024-10-05 21:00:00', NULL, '2024-10-05 21:00:00');

-- User 15 (Matthew Cox) - Published Journey
INSERT INTO journeys (journey_id, user_id, title, `description`, `start_date`, create_time, update_by, update_time, `status`, `hidden`, cover_image) VALUES
(30, 15, 'American Southwest Road Trip', 'Desert landscapes and national parks', '2024-05-15', '2024-05-20 10:00:00', NULL, '2024-05-20 10:00:00', 'published', FALSE, 'uploads/events/antelope_canyon_beams.jpg');

INSERT INTO events (event_id, journey_id, user_id, location_id, title, `description`, `start_date`, end_date, create_time, update_by, update_time) VALUES
(146, 30, 15, 14, 'Antelope Canyon', 'Spectacular slot canyon photography', '2024-05-15 11:00:00', '2024-05-15 15:00:00', '2024-05-20 10:30:00', NULL, '2024-05-20 10:30:00'),
(147, 30, 15, 14, 'Monument Valley', 'Iconic desert landscape and buttes', '2024-05-17 07:00:00', '2024-05-17 19:00:00', '2024-05-20 12:00:00', NULL, '2024-05-20 12:00:00'),
(148, 30, 15, 14, 'Zion National Park', 'Red rock canyons and hiking trails', '2024-05-19 08:00:00', '2024-05-19 17:00:00', '2024-05-20 13:45:00', NULL, '2024-05-20 13:45:00'),
(149, 30, 15, 14, 'Bryce Canyon', 'Unique hoodoo rock formations', '2024-05-21 06:00:00', '2024-05-21 16:00:00', '2024-05-20 15:30:00', NULL, '2024-05-20 15:30:00'),
(150, 30, 15, 14, 'Death Valley', 'Extreme desert environment exploration', '2024-05-23 05:00:00', '2024-05-23 12:00:00', '2024-05-20 17:15:00', NULL, '2024-05-20 17:15:00');

-- User 16 (Ella Richardson) - Private Journey
INSERT INTO journeys (journey_id, user_id, title, `description`, `start_date`, create_time, update_by, update_time, `status`, `hidden`) VALUES
(31, 16, 'Personal Spiritual Journey', 'Private spiritual retreat and self-discovery', '2024-02-01', '2024-02-05 15:20:00', NULL, '2024-02-05 15:20:00', 'private', FALSE);

INSERT INTO events (event_id, journey_id, user_id, location_id, title, `description`, `start_date`, end_date, create_time, update_by, update_time) VALUES
(151, 31, 16, 1, 'Maori Cultural Center', 'Learning about indigenous spirituality', '2024-02-01 10:00:00', '2024-02-01 16:00:00', '2024-02-05 15:50:00', NULL, '2024-02-05 15:50:00'),
(152, 31, 16, 1, 'Hot Springs Meditation', 'Thermal pools and mindfulness practice', '2024-02-02 07:00:00', '2024-02-02 12:00:00', '2024-02-05 17:30:00', NULL, '2024-02-05 17:30:00'),
(153, 31, 16, 1, 'Forest Sanctuary', 'Silent retreat in native forest', '2024-02-03 09:00:00', '2024-02-03 17:00:00', '2024-02-05 19:00:00', NULL, '2024-02-05 19:00:00'),
(154, 31, 16, 1, 'Mountain Pilgrimage', 'Sacred mountain climbing experience', '2024-02-04 05:00:00', '2024-02-04 18:00:00', '2024-02-05 20:45:00', NULL, '2024-02-05 20:45:00'),
(155, 31, 16, 1, 'Reflection Ceremony', 'Personal ceremony and gratitude practice', '2024-02-05 08:00:00', '2024-02-05 14:00:00', '2024-02-05 22:15:00', NULL, '2024-02-05 22:15:00');

-- User 16 (Ella Richardson) - Published Journey
INSERT INTO journeys (journey_id, user_id, title, `description`, `start_date`, create_time, update_by, update_time, `status`, `hidden`, cover_image) VALUES
(32, 16, 'Kiwi Adventure Sports', 'Adrenaline activities across New Zealand', '2024-01-10', '2024-01-15 11:30:00', NULL, '2024-01-15 11:30:00', 'published', FALSE, 'uploads/events/bungee_jumping_gorge.jpg');

INSERT INTO events (event_id, journey_id, user_id, location_id, title, `description`, `start_date`, end_date, create_time, update_by, update_time) VALUES
(156, 32, 16, 1, 'Bungee Jumping', 'AJ Hackett Kawarau Gorge bungee', '2024-01-10 14:00:00', '2024-01-10 16:00:00', '2024-01-15 12:00:00', NULL, '2024-01-15 12:00:00'),
(157, 32, 16, 1, 'White Water Rafting', 'Shotover River rapids adventure', '2024-01-12 09:00:00', '2024-01-12 15:00:00', '2024-01-15 13:30:00', NULL, '2024-01-15 13:30:00'),
(158, 32, 16, 1, 'Skydiving Experience', 'Tandem jump over Southern Alps', '2024-01-14 10:00:00', '2024-01-14 14:00:00', '2024-01-15 15:00:00', NULL, '2024-01-15 15:00:00'),
(159, 32, 16, 1, 'Cave Exploring', 'Waitomo glowworm caves adventure', '2024-01-16 11:00:00', '2024-01-16 17:00:00', '2024-01-15 16:45:00', NULL, '2024-01-15 16:45:00'),
(160, 32, 16, 1, 'Jet Boat Ride', 'High-speed boat through narrow canyons', '2024-01-18 13:00:00', '2024-01-18 15:00:00', '2024-01-15 18:30:00', NULL, '2024-01-15 18:30:00');

-- User 17 (Joseph Howard) - Private Journey
INSERT INTO journeys (journey_id, user_id, title, `description`, `start_date`, create_time, update_by, update_time, `status`, `hidden`) VALUES
(33, 17, 'Secret Tech Innovation Lab', 'Private tech project development retreat', '2024-11-01', '2024-11-05 16:40:00', NULL, '2024-11-05 16:40:00', 'private', FALSE);

INSERT INTO events (event_id, journey_id, user_id, location_id, title, `description`, `start_date`, end_date, create_time, update_by, update_time) VALUES
(161, 33, 17, 14, 'Lab Setup', 'Establishing private development environment', '2024-11-01 09:00:00', '2024-11-01 17:00:00', '2024-11-05 17:10:00', NULL, '2024-11-05 17:10:00'),
(162, 33, 17, 14, 'Prototype Development', 'Building initial concept prototype', '2024-11-02 08:00:00', '2024-11-02 20:00:00', '2024-11-05 18:45:00', NULL, '2024-11-05 18:45:00'),
(163, 33, 17, 14, 'Testing Phase', 'Rigorous testing and debugging', '2024-11-03 10:00:00', '2024-11-03 18:00:00', '2024-11-05 20:15:00', NULL, '2024-11-05 20:15:00'),
(164, 33, 17, 14, 'Market Research', 'Private market analysis and validation', '2024-11-04 09:00:00', '2024-11-04 16:00:00', '2024-11-05 21:50:00', NULL, '2024-11-05 21:50:00'),
(165, 33, 17, 14, 'Patent Documentation', 'Intellectual property documentation', '2024-11-05 08:00:00', '2024-11-05 15:00:00', '2024-11-05 23:20:00', NULL, '2024-11-05 23:20:00');

-- User 17 (Joseph Howard) - Published Journey
INSERT INTO journeys (journey_id, user_id, title, `description`, `start_date`, create_time, update_by, update_time, `status`, `hidden`, cover_image) VALUES
(34, 17, 'West Coast Tech Hubs', 'Exploring innovation centers from Seattle to LA', '2024-08-01', '2024-08-05 13:25:00', NULL, '2024-08-05 13:25:00', 'published', FALSE, 'uploads/events/seattle_microsoft_campus.jpg');

INSERT INTO events (event_id, journey_id, user_id, location_id, title, `description`, `start_date`, end_date, create_time, update_by, update_time) VALUES
(166, 34, 17, 14, 'Seattle Microsoft Campus', 'Exploring the Microsoft headquarters', '2024-08-01 10:00:00', '2024-08-01 16:00:00', '2024-08-05 14:00:00', NULL, '2024-08-05 14:00:00'),
(167, 34, 17, 14, 'Portland Tech Scene', 'Nike headquarters and startup ecosystem', '2024-08-03 09:00:00', '2024-08-03 17:00:00', '2024-08-05 15:30:00', NULL, '2024-08-05 15:30:00'),
(168, 34, 17, 14, 'Silicon Valley Giants', 'Facebook, Google, and Apple campuses', '2024-08-05 08:00:00', '2024-08-05 18:00:00', '2024-08-05 17:00:00', NULL, '2024-08-05 17:00:00'),
(169, 34, 17, 14, 'LA Entertainment Tech', 'Hollywood meets technology', '2024-08-07 11:00:00', '2024-08-07 19:00:00', '2024-08-05 18:45:00', NULL, '2024-08-05 18:45:00'),
(170, 34, 17, 14, 'San Diego Biotech', 'Biotechnology and medical innovation', '2024-08-09 09:00:00', '2024-08-09 17:00:00', '2024-08-05 20:15:00', NULL, '2024-08-05 20:15:00');

-- User 18 (Avery Cook) - Private Journey
INSERT INTO journeys (journey_id, user_id, title, `description`, `start_date`, create_time, update_by, update_time, `status`, `hidden`) VALUES
(35, 18, 'Culinary Masterclass Retreat', 'Private cooking skills intensive', '2024-09-15', '2024-09-20 12:10:00', NULL, '2024-09-20 12:10:00', 'private', FALSE);

INSERT INTO events (event_id, journey_id, user_id, location_id, title, `description`, `start_date`, end_date, create_time, update_by, update_time) VALUES
(171, 35, 18, 6, 'French Technique Workshop', 'Classic French cooking fundamentals', '2024-09-15 09:00:00', '2024-09-15 17:00:00', '2024-09-20 12:40:00', NULL, '2024-09-20 12:40:00'),
(172, 35, 18, 2, 'Michelin Star Experience', 'Working with renowned London chef', '2024-09-16 08:00:00', '2024-09-16 20:00:00', '2024-09-20 14:15:00', NULL, '2024-09-20 14:15:00'),
(173, 35, 18, 5, 'Farm to Table', 'Irish organic farm cooking experience', '2024-09-17 07:00:00', '2024-09-17 19:00:00', '2024-09-20 15:50:00', NULL, '2024-09-20 15:50:00'),
(174, 35, 18, 24, 'Whisky Pairing', 'Scottish cuisine and whisky combinations', '2024-09-18 10:00:00', '2024-09-18 18:00:00', '2024-09-20 17:30:00', NULL, '2024-09-20 17:30:00'),
(175, 35, 18, 6, 'Personal Menu Creation', 'Developing signature dishes', '2024-09-19 09:00:00', '2024-09-19 16:00:00', '2024-09-20 19:00:00', NULL, '2024-09-20 19:00:00');

-- User 18 (Avery Cook) - Published Journey
INSERT INTO journeys (journey_id, user_id, title, `description`, `start_date`, create_time, update_by, update_time, `status`, `hidden`, cover_image) VALUES
(36, 18, 'British Isles Pub Crawl', 'Traditional pubs and local brews', '2024-06-10', '2024-06-15 14:30:00', NULL, '2024-06-15 14:30:00', 'published', FALSE, 'uploads/events/historic_london_pubs.jpg');

INSERT INTO events (event_id, journey_id, user_id, location_id, title, `description`, `start_date`, end_date, create_time, update_by, update_time) VALUES
(176, 36, 18, 2, 'Historic London Pubs', 'Ye Olde Cheshire Cheese and ancient taverns', '2024-06-10 16:00:00', '2024-06-10 22:00:00', '2024-06-15 15:00:00', NULL, '2024-06-15 15:00:00'),
(177, 36, 18, 5, 'Dublin Traditional Pubs', 'Temple Bar and Guinness heritage', '2024-06-12 17:00:00', '2024-06-12 23:00:00', '2024-06-15 16:45:00', NULL, '2024-06-15 16:45:00'),
(178, 36, 18, 24, 'Edinburgh Whisky Bars', 'Royal Mile whisky tasting tour', '2024-06-14 15:00:00', '2024-06-14 21:00:00', '2024-06-15 18:20:00', NULL, '2024-06-15 18:20:00'),
(179, 36, 18, 6, 'Cotswolds Country Pubs', 'Rural English pub culture', '2024-06-16 12:00:00', '2024-06-16 20:00:00', '2024-06-15 19:55:00', NULL, '2024-06-15 19:55:00'),
(180, 36, 18, 5, 'Cork City Microbreweries', 'Irish craft beer revolution', '2024-06-18 14:00:00', '2024-06-18 22:00:00', '2024-06-15 21:30:00', NULL, '2024-06-15 21:30:00');

-- User 19 (Samuel Bell) - Private Journey
INSERT INTO journeys (journey_id, user_id, title, `description`, `start_date`, create_time, update_by, update_time, `status`, `hidden`) VALUES
(37, 19, 'Personal Fitness Challenge', 'Solo endurance training expedition', '2024-07-01', '2024-07-05 08:50:00', NULL, '2024-07-05 08:50:00', 'private', FALSE);

INSERT INTO events (event_id, journey_id, user_id, location_id, title, `description`, `start_date`, end_date, create_time, update_by, update_time) VALUES
(181, 37, 19, 20, 'Base Camp Setup', 'Establishing training base in Canadian Rockies', '2024-07-01 06:00:00', '2024-07-01 12:00:00', '2024-07-05 09:20:00', NULL, '2024-07-05 09:20:00'),
(182, 37, 19, 20, 'High Altitude Training', 'Altitude acclimatization exercises', '2024-07-02 05:00:00', '2024-07-02 18:00:00', '2024-07-05 11:00:00', NULL, '2024-07-05 11:00:00'),
(183, 37, 19, 20, 'Endurance Challenge', '50km mountain trail run', '2024-07-03 04:00:00', '2024-07-03 16:00:00', '2024-07-05 12:45:00', NULL, '2024-07-05 12:45:00'),
(184, 37, 19, 20, 'Recovery Session', 'Cold water therapy and meditation', '2024-07-04 08:00:00', '2024-07-04 14:00:00', '2024-07-05 14:30:00', NULL, '2024-07-05 14:30:00'),
(185, 37, 19, 20, 'Final Assessment', 'Fitness goals evaluation and planning', '2024-07-05 09:00:00', '2024-07-05 15:00:00', '2024-07-05 16:15:00', NULL, '2024-07-05 16:15:00');

-- User 19 (Samuel Bell) - Published Journey
INSERT INTO journeys (journey_id, user_id, title, `description`, `start_date`, create_time, update_by, update_time, `status`, `hidden`, cover_image) VALUES
(38, 19, 'Northern Wilderness Adventure', 'Extreme cold weather exploration', '2024-01-15', '2024-01-20 10:40:00', NULL, '2024-01-20 10:40:00', 'published', FALSE, 'uploads/events/winter_survival_training.jpg');

INSERT INTO events (event_id, journey_id, user_id, location_id, title, `description`, `start_date`, end_date, create_time, update_by, update_time) VALUES
(186, 38, 19, 20, 'Winter Survival Training', 'Cold weather survival skills', '2024-01-15 08:00:00', '2024-01-15 17:00:00', '2024-01-20 11:15:00', NULL, '2024-01-20 11:15:00'),
(187, 38, 19, 20, 'Ice Climbing', 'Frozen waterfall climbing expedition', '2024-01-17 07:00:00', '2024-01-17 16:00:00', '2024-01-20 12:50:00', NULL, '2024-01-20 12:50:00'),
(188, 38, 19, 20, 'Aurora Tracking', 'Northern lights photography expedition', '2024-01-19 20:00:00', '2024-01-20 03:00:00', '2024-01-20 14:25:00', NULL, '2024-01-20 14:25:00'),
(189, 38, 19, 20, 'Snowshoe Trekking', 'Traditional snowshoe hiking', '2024-01-21 09:00:00', '2024-01-21 17:00:00', '2024-01-20 16:00:00', NULL, '2024-01-20 16:00:00'),
(190, 38, 19, 20, 'Wildlife Tracking', 'Arctic animal behavior observation', '2024-01-23 06:00:00', '2024-01-23 15:00:00', '2024-01-20 17:45:00', NULL, '2024-01-20 17:45:00');

-- User 20 (Luna Murphy) - Private Journey
INSERT INTO journeys (journey_id, user_id, title, `description`, `start_date`, create_time, update_by, update_time, `status`, `hidden`) VALUES
(39, 20, 'Ancestral Heritage Research', 'Private family history investigation', '2024-11-10', '2024-11-15 13:55:00', NULL, '2024-11-15 13:55:00', 'private', FALSE);

INSERT INTO events (event_id, journey_id, user_id, location_id, title, `description`, `start_date`, end_date, create_time, update_by, update_time) VALUES
(191, 39, 20, 6, 'Genealogy Archives', 'Researching family records in London', '2024-11-10 10:00:00', '2024-11-10 16:00:00', '2024-11-15 14:25:00', NULL, '2024-11-15 14:25:00'),
(192, 39, 20, 5, 'Irish Parish Records', 'Tracing Irish ancestors in County Cork', '2024-11-11 09:00:00', '2024-11-11 17:00:00', '2024-11-15 16:00:00', NULL, '2024-11-15 16:00:00'),
(193, 39, 20, 24, 'Highland Clan History', 'Scottish clan research in Edinburgh', '2024-11-12 11:00:00', '2024-11-12 18:00:00', '2024-11-15 17:40:00', NULL, '2024-11-15 17:40:00'),
(194, 39, 20, 15, 'Eastern European Roots', 'Polish ancestry research in Krakow', '2024-11-13 08:00:00', '2024-11-13 16:00:00', '2024-11-15 19:20:00', NULL, '2024-11-15 19:20:00'),
(195, 39, 20, 6, 'DNA Analysis Meeting', 'Genetic genealogy consultation', '2024-11-14 14:00:00', '2024-11-14 17:00:00', '2024-11-15 21:00:00', NULL, '2024-11-15 21:00:00');

-- User 20 (Luna Murphy) - Published Journey
INSERT INTO journeys (journey_id, user_id, title, `description`, `start_date`, create_time, update_by, update_time, `status`, `hidden`, cover_image) VALUES
(40, 20, 'European Art Museums Tour', 'Masterpieces across European capitals', '2024-04-20', '2024-04-25 15:30:00', NULL, '2024-04-25 15:30:00', 'published', FALSE, 'uploads/events/british_museum_highlights.jpg');

INSERT INTO events (event_id, journey_id, user_id, location_id, title, `description`, `start_date`, end_date, create_time, update_by, update_time) VALUES
(196, 40, 20, 2, 'British Museum Highlights', 'Ancient civilizations and artifacts', '2024-04-20 10:00:00', '2024-04-20 16:00:00', '2024-04-25 16:00:00', NULL, '2024-04-25 16:00:00'),
(197, 40, 20, 6, 'Tate Modern Contemporary', 'Modern and contemporary art exploration', '2024-04-21 11:00:00', '2024-04-21 17:00:00', '2024-04-25 17:35:00', NULL, '2024-04-25 17:35:00'),
(198, 40, 20, 15, 'Warsaw National Museum', 'Polish art and cultural heritage', '2024-04-22 09:00:00', '2024-04-22 15:00:00', '2024-04-25 19:10:00', NULL, '2024-04-25 19:10:00'),
(199, 40, 20, 22, 'Ljubljana Modern Gallery', 'Slovenian contemporary art scene', '2024-04-23 10:00:00', '2024-04-23 16:00:00', '2024-04-25 20:45:00', NULL, '2024-04-25 20:45:00'),
(200, 40, 20, 6, 'National Gallery London', 'Renaissance and classical masterpieces', '2024-04-24 09:00:00', '2024-04-24 17:00:00', '2024-04-25 22:20:00', NULL, '2024-04-25 22:20:00');

-- User 21 (Admin1 - Liam Walker) - Published Journey
INSERT INTO journeys (journey_id, user_id, title, `description`, `start_date`, create_time, update_by, update_time, `status`, `hidden`, cover_image) VALUES
(41, 21, 'Administrative World Tour', 'Global business and cultural exchange journey', '2024-01-05', '2024-01-10 09:30:00', NULL, '2024-01-10 09:30:00', 'public', FALSE, 'uploads/journey/london_business_summit.jpg');

INSERT INTO events (event_id, journey_id, user_id, location_id, title, `description`, `start_date`, end_date, create_time, update_by, update_time) VALUES
(201, 41, 21, 2, 'London Business Summit', 'International business conference and networking', '2024-01-05 09:00:00', '2024-01-05 18:00:00', '2024-01-10 10:00:00', NULL, '2024-01-10 10:00:00'),
(202, 41, 21, 25, 'Singapore Trade Fair', 'Asian market expansion opportunities', '2024-01-07 10:00:00', '2024-01-07 17:00:00', '2024-01-10 11:30:00', NULL, '2024-01-10 11:30:00'),
(203, 41, 21, 3, 'Tokyo Technology Exchange', 'Innovation and digital transformation', '2024-01-09 08:00:00', '2024-01-09 16:00:00', '2024-01-10 13:00:00', NULL, '2024-01-10 13:00:00'),
(204, 41, 21, 14, 'New York Financial District', 'Wall Street and financial markets tour', '2024-01-11 09:00:00', '2024-01-11 15:00:00', '2024-01-10 14:45:00', NULL, '2024-01-10 14:45:00'),
(205, 41, 21, 11, 'Sydney Operations Center', 'Regional headquarters establishment', '2024-01-13 10:00:00', '2024-01-13 16:00:00', '2024-01-10 16:15:00', NULL, '2024-01-10 16:15:00');

-- User 22 (Admin2 - Emma Roberts) - Published Journey
INSERT INTO journeys (journey_id, user_id, title, `description`, `start_date`, create_time, update_by, update_time, `status`, `hidden`, cover_image) VALUES
(42, 22, 'Cultural Heritage Expedition', 'UNESCO World Heritage sites exploration', '2024-02-10', '2024-02-15 14:20:00', NULL, '2024-02-15 14:20:00', 'public', FALSE, 'uploads/journey/parthenon_acropolis.jpg');

INSERT INTO events (event_id, journey_id, user_id, location_id, title, `description`, `start_date`, end_date, create_time, update_by, update_time) VALUES
(206, 42, 22, 12, 'Parthenon and Acropolis', 'Ancient Greek architectural marvels', '2024-02-10 08:00:00', '2024-02-10 16:00:00', '2024-02-15 14:50:00', NULL, '2024-02-15 14:50:00'),
(207, 42, 22, 6, 'Stonehenge Mystery', 'Prehistoric monument and archaeology', '2024-02-12 10:00:00', '2024-02-12 14:00:00', '2024-02-15 16:25:00', NULL, '2024-02-15 16:25:00'),
(208, 42, 22, 15, 'Auschwitz Memorial', 'Historical remembrance and education', '2024-02-14 09:00:00', '2024-02-14 17:00:00', '2024-02-15 18:00:00', NULL, '2024-02-15 18:00:00'),
(209, 42, 22, 9, 'Great Wall of China', 'Ancient fortification and engineering marvel', '2024-02-16 07:00:00', '2024-02-16 15:00:00', '2024-02-15 19:30:00', NULL, '2024-02-15 19:30:00'),
(210, 42, 22, 19, 'Valletta Historic City', 'Medieval fortress city of Malta', '2024-02-18 11:00:00', '2024-02-18 18:00:00', '2024-02-15 21:15:00', NULL, '2024-02-15 21:15:00');

-- User 23 (Admin3 - Logan Long) - Published Journey
INSERT INTO journeys (journey_id, user_id, title, `description`, `start_date`, create_time, update_by, update_time, `status`, `hidden`, cover_image) VALUES
(43, 23, 'Strategic Planning Retreat', 'Global corporate strategy development', '2024-03-15', '2024-03-20 11:45:00', NULL, '2024-03-20 11:45:00', 'public', FALSE, 'uploads/journey/ljubljana_innovation_hub.jpg');

INSERT INTO events (event_id, journey_id, user_id, location_id, title, `description`, `start_date`, end_date, create_time, update_by, update_time) VALUES
(211, 43, 23, 22, 'Ljubljana Innovation Hub', 'European startup ecosystem analysis', '2024-03-15 09:00:00', '2024-03-15 17:00:00', '2024-03-20 12:15:00', NULL, '2024-03-20 12:15:00'),
(212, 43, 23, 14, 'Silicon Valley Research', 'Technology trends and market analysis', '2024-03-17 08:00:00', '2024-03-17 18:00:00', '2024-03-20 13:45:00', NULL, '2024-03-20 13:45:00'),
(213, 43, 23, 25, 'Singapore Fintech Summit', 'Financial technology innovations', '2024-03-19 10:00:00', '2024-03-19 16:00:00', '2024-03-20 15:30:00', NULL, '2024-03-20 15:30:00'),
(214, 43, 23, 2, 'London Strategy Workshop', 'International expansion planning', '2024-03-21 09:00:00', '2024-03-21 15:00:00', '2024-03-20 17:00:00', NULL, '2024-03-20 17:00:00'),
(215, 43, 23, 20, 'Toronto Executive Retreat', 'Leadership development and team building', '2024-03-23 08:00:00', '2024-03-23 20:00:00', '2024-03-20 18:45:00', NULL, '2024-03-20 18:45:00');

-- User 24 (Admin4 - Grace Ramirez) - Published Journey
INSERT INTO journeys (journey_id, user_id, title, `description`, `start_date`, create_time, update_by, update_time, `status`, `hidden`, cover_image) VALUES
(44, 24, 'Global Sustainability Initiative', 'Environmental conservation and green technology', '2024-04-20', '2024-04-25 13:10:00', NULL, '2024-04-25 13:10:00', 'public', FALSE, 'uploads/journey/nz_renewable_energy.jpg');

INSERT INTO events (event_id, journey_id, user_id, location_id, title, `description`, `start_date`, end_date, create_time, update_by, update_time) VALUES
(216, 44, 24, 1, 'New Zealand Renewable Energy', 'Geothermal and wind power facilities', '2024-04-20 09:00:00', '2024-04-20 17:00:00', '2024-04-25 13:40:00', NULL, '2024-04-25 13:40:00'),
(217, 44, 24, 8, 'Siberian Forest Conservation', 'Taiga preservation and carbon sequestration', '2024-04-22 07:00:00', '2024-04-22 19:00:00', '2024-04-25 15:20:00', NULL, '2024-04-25 15:20:00'),
(218, 44, 24, 11, 'Australian Solar Farms', 'Large-scale solar energy projects', '2024-04-24 08:00:00', '2024-04-24 16:00:00', '2024-04-25 16:55:00', NULL, '2024-04-25 16:55:00'),
(219, 44, 24, 20, 'Canadian Hydroelectric', 'Clean hydropower generation systems', '2024-04-26 10:00:00', '2024-04-26 18:00:00', '2024-04-25 18:30:00', NULL, '2024-04-25 18:30:00'),
(220, 44, 24, 14, 'California Green Tech', 'Silicon Valley sustainability innovations', '2024-04-28 09:00:00', '2024-04-28 17:00:00', '2024-04-25 20:15:00', NULL, '2024-04-25 20:15:00');

-- User 25 (Admin5 - Tyler Moore) - Published Journey
INSERT INTO journeys (journey_id, user_id, title, `description`, `start_date`, create_time, update_by, update_time, `status`, `hidden`, cover_image) VALUES
(45, 25, 'Digital Transformation Journey', 'Technology implementation across global offices', '2024-05-10', '2024-05-15 16:25:00', NULL, '2024-05-15 16:25:00', 'public', FALSE, 'uploads/journey/tokyo_smart_city.jpg');

INSERT INTO events (event_id, journey_id, user_id, location_id, title, `description`, `start_date`, end_date, create_time, update_by, update_time) VALUES
(221, 45, 25, 3, 'Tokyo Smart City Tour', 'IoT and AI integration in urban planning', '2024-05-10 08:00:00', '2024-05-10 18:00:00', '2024-05-15 16:55:00', NULL, '2024-05-15 16:55:00'),
(222, 45, 25, 24, 'Edinburgh Data Centers', 'Cloud infrastructure and data management', '2024-05-12 09:00:00', '2024-05-12 17:00:00', '2024-05-15 18:30:00', NULL, '2024-05-15 18:30:00'),
(223, 45, 25, 5, 'Dublin Tech Campus', 'European headquarters technology upgrade', '2024-05-14 10:00:00', '2024-05-14 16:00:00', '2024-05-15 20:00:00', NULL, '2024-05-15 20:00:00'),
(224, 45, 25, 13, 'Malaysia Manufacturing 4.0', 'Industrial automation and robotics', '2024-05-16 08:00:00', '2024-05-16 18:00:00', '2024-05-15 21:45:00', NULL, '2024-05-15 21:45:00'),
(225, 45, 25, 16, 'New York Cybersecurity Hub', 'Security protocols and threat management', '2024-05-18 09:00:00', '2024-05-18 17:00:00', '2024-05-15 23:20:00', NULL, '2024-05-15 23:20:00');

-- User 26 (Editor1 - Noah Smith) - Published Journey
INSERT INTO journeys (journey_id, user_id, title, `description`, `start_date`, create_time, update_by, update_time, `status`, `hidden`, cover_image) VALUES
(46, 26, 'Literary Landscapes Tour', 'Famous authors and literary destinations', '2024-06-01', '2024-06-05 12:40:00', NULL, '2024-06-05 12:40:00', 'public', FALSE, 'uploads/journey/shakespeare_country.jpg');

INSERT INTO events (event_id, journey_id, user_id, location_id, title, `description`, `start_date`, end_date, create_time, update_by, update_time) VALUES
(226, 46, 26, 6, 'Shakespeare Country', 'Stratford-upon-Avon and Globe Theatre', '2024-06-01 10:00:00', '2024-06-01 18:00:00', '2024-06-05 13:10:00', NULL, '2024-06-05 13:10:00'),
(227, 46, 26, 5, 'Joyce Dublin Walk', 'Bloomsday and Ulysses locations', '2024-06-03 09:00:00', '2024-06-03 17:00:00', '2024-06-05 14:45:00', NULL, '2024-06-05 14:45:00'),
(228, 46, 26, 24, 'Burns Scotland Heritage', 'Robert Burns birthplace and monuments', '2024-06-05 08:00:00', '2024-06-05 16:00:00', '2024-06-05 16:20:00', NULL, '2024-06-05 16:20:00'),
(229, 46, 26, 2, 'Dickens London Trail', 'Victorian London and author landmarks', '2024-06-07 11:00:00', '2024-06-07 19:00:00', '2024-06-05 18:00:00', NULL, '2024-06-05 18:00:00'),
(230, 46, 26, 6, 'Brontë Yorkshire Moors', 'Haworth parsonage and windswept landscapes', '2024-06-09 09:00:00', '2024-06-09 17:00:00', '2024-06-05 19:35:00', NULL, '2024-06-05 19:35:00');

-- User 27 (Editor2 - Olivia Johnson) - Published Journey
INSERT INTO journeys (journey_id, user_id, title, `description`, `start_date`, create_time, update_by, update_time, `status`, `hidden`, cover_image) VALUES
(47, 27, 'Art History Masterpiece Tour', 'Renaissance to modern art across Europe', '2024-07-15', '2024-07-20 15:15:00', NULL, '2024-07-20 15:15:00', 'public', FALSE, 'uploads/journey/national_gallery_london.jpg');

INSERT INTO events (event_id, journey_id, user_id, location_id, title, `description`, `start_date`, end_date, create_time, update_by, update_time) VALUES
(231, 47, 27, 2, 'National Gallery London', 'Van Gogh, Monet, and Turner masterpieces', '2024-07-15 10:00:00', '2024-07-15 17:00:00', '2024-07-20 15:45:00', NULL, '2024-07-20 15:45:00'),
(232, 47, 27, 6, 'Tate Britain Collection', 'British art from 1500 to present day', '2024-07-17 09:00:00', '2024-07-17 16:00:00', '2024-07-20 17:30:00', NULL, '2024-07-20 17:30:00'),
(233, 47, 27, 22, 'Ljubljana Modern Gallery', 'Contemporary Slovenian and Balkan art', '2024-07-19 11:00:00', '2024-07-19 17:00:00', '2024-07-20 19:00:00', NULL, '2024-07-20 19:00:00'),
(234, 47, 27, 15, 'Krakow National Museum', 'Polish medieval and renaissance art', '2024-07-21 10:00:00', '2024-07-21 16:00:00', '2024-07-20 20:45:00', NULL, '2024-07-20 20:45:00'),
(235, 47, 27, 12, 'Athens Byzantine Museum', 'Orthodox Christian art and iconography', '2024-07-23 09:00:00', '2024-07-23 15:00:00', '2024-07-20 22:20:00', NULL, '2024-07-20 22:20:00');

-- User 28 (Editor3 - Elijah Brown) - Published Journey
INSERT INTO journeys (journey_id, user_id, title, `description`, `start_date`, create_time, update_by, update_time, `status`, `hidden`, cover_image) VALUES
(48, 28, 'Documentary Film Locations', 'Behind the scenes of nature documentaries', '2024-08-10', '2024-08-15 10:30:00', NULL, '2024-08-15 10:30:00', 'public', FALSE, 'uploads/journey/reef_marine_life.jpg');

INSERT INTO events (event_id, journey_id, user_id, location_id, title, `description`, `start_date`, end_date, create_time, update_by, update_time) VALUES
(236, 48, 28, 11, 'Great Barrier Reef Filming', 'Underwater cinematography and marine life', '2024-08-10 06:00:00', '2024-08-10 18:00:00', '2024-08-15 11:00:00', NULL, '2024-08-15 11:00:00'),
(237, 48, 28, 20, 'Arctic Wildlife Documentation', 'Polar bear and arctic fox behavior', '2024-08-12 05:00:00', '2024-08-12 19:00:00', '2024-08-15 12:45:00', NULL, '2024-08-15 12:45:00'),
(238, 48, 28, 8, 'Siberian Tiger Reserve', 'Endangered species conservation filming', '2024-08-14 07:00:00', '2024-08-14 17:00:00', '2024-08-15 14:20:00', NULL, '2024-08-15 14:20:00'),
(239, 48, 28, 9, 'Yangtze River Journey', 'Environmental changes and wildlife', '2024-08-16 08:00:00', '2024-08-16 20:00:00', '2024-08-15 16:00:00', NULL, '2024-08-15 16:00:00'),
(240, 48, 28, 21, 'Amazon Rainforest Canopy', 'Tropical biodiversity and climate research', '2024-08-18 06:00:00', '2024-08-18 18:00:00', '2024-08-15 17:30:00', NULL, '2024-08-15 17:30:00');

-- User 29 (Editor4 - David Bailey) - Published Journey
INSERT INTO journeys (journey_id, user_id, title, `description`, `start_date`, create_time, update_by, update_time, `status`, `hidden`, cover_image) VALUES
(49, 29, 'Historical Battlefields Study', 'Military history and strategic analysis', '2024-09-05', '2024-09-10 14:50:00', NULL, '2024-09-10 14:50:00', 'public', FALSE, 'uploads/journey/normandy_memorial.jpg');

INSERT INTO events (event_id, journey_id, user_id, location_id, title, `description`, `start_date`, end_date, create_time, update_by, update_time) VALUES
(241, 49, 29, 6, 'Normandy D-Day Beaches', 'Operation Overlord landing sites', '2024-09-05 08:00:00', '2024-09-05 18:00:00', '2024-09-10 15:20:00', NULL, '2024-09-10 15:20:00'),
(242, 49, 29, 15, 'Westerplatte Memorial', 'WWII outbreak location in Gdansk', '2024-09-07 09:00:00', '2024-09-07 17:00:00', '2024-09-10 17:00:00', NULL, '2024-09-10 17:00:00'),
(243, 49, 29, 8, 'Stalingrad Battlefield', 'Turning point of Eastern Front', '2024-09-09 10:00:00', '2024-09-09 16:00:00', '2024-09-10 18:35:00', NULL, '2024-09-10 18:35:00'),
(244, 49, 29, 6, 'Waterloo Battlefield', 'Napoleon final defeat site', '2024-09-11 09:00:00', '2024-09-11 15:00:00', '2024-09-10 20:15:00', NULL, '2024-09-10 20:15:00'),
(245, 49, 29, 14, 'Gettysburg National Park', 'American Civil War pivotal battle', '2024-09-13 08:00:00', '2024-09-13 17:00:00', '2024-09-10 21:45:00', NULL, '2024-09-10 21:45:00');

-- User 30 (Editor5 - Scarlett Perry) - Published Journey
INSERT INTO journeys (journey_id, user_id, title, `description`, `start_date`, create_time, update_by, update_time, `status`, `hidden`, cover_image) VALUES
(50, 30, 'Fashion Capitals Exploration', 'Global fashion weeks and design districts', '2024-10-15', '2024-10-20 16:40:00', NULL, '2024-10-20 16:40:00', 'public', FALSE, 'uploads/journey/tokyo_harajuku_style.jpg');

INSERT INTO events (event_id, journey_id, user_id, location_id, title, `description`, `start_date`, end_date, create_time, update_by, update_time) VALUES
(246, 50, 30, 2, 'London Fashion Week', 'British designers and emerging talent', '2024-10-15 09:00:00', '2024-10-15 22:00:00', '2024-10-20 17:10:00', NULL, '2024-10-20 17:10:00'),
(247, 50, 30, 16, 'New York Fashion District', 'Garment district and flagship stores', '2024-10-17 10:00:00', '2024-10-17 20:00:00', '2024-10-20 18:50:00', NULL, '2024-10-20 18:50:00'),
(248, 50, 30, 3, 'Tokyo Harajuku Style', 'Street fashion and avant-garde design', '2024-10-19 11:00:00', '2024-10-19 19:00:00', '2024-10-20 20:25:00', NULL, '2024-10-20 20:25:00'),
(249, 50, 30, 25, 'Singapore Design Hub', 'Asian fashion innovation center', '2024-10-21 09:00:00', '2024-10-21 17:00:00', '2024-10-20 22:00:00', NULL, '2024-10-20 22:00:00'),
(250, 50, 30, 11, 'Melbourne Fashion Precinct', 'Australian designers and sustainable fashion', '2024-10-23 10:00:00', '2024-10-23 18:00:00', '2024-10-20 23:35:00', NULL, '2024-10-20 23:35:00');

-- User 31 (SupportTech1 - Lucas Allen) - Published Journey
INSERT INTO journeys (journey_id, user_id, title, `description`, `start_date`, create_time, update_by, update_time, `status`, `hidden`, cover_image) VALUES
(51, 31, 'Technical Support World Tour', 'Global customer service excellence study', '2024-11-01', '2024-11-05 09:15:00', NULL, '2024-11-05 09:15:00', 'public', FALSE, 'uploads/journey/singapore_call_center.jpg');

INSERT INTO events (event_id, journey_id, user_id, location_id, title, `description`, `start_date`, end_date, create_time, update_by, update_time) VALUES
(251, 51, 31, 25, 'Singapore Call Center Excellence', 'Best practices in customer service', '2024-11-01 08:00:00', '2024-11-01 18:00:00', '2024-11-05 09:45:00', NULL, '2024-11-05 09:45:00'),
(252, 51, 31, 5, 'Dublin Tech Support Hub', 'European support operations analysis', '2024-11-03 09:00:00', '2024-11-03 17:00:00', '2024-11-05 11:30:00', NULL, '2024-11-05 11:30:00'),
(253, 51, 31, 3, 'Tokyo Customer Experience', 'Japanese hospitality and service culture', '2024-11-05 08:00:00', '2024-11-05 16:00:00', '2024-11-05 13:00:00', NULL, '2024-11-05 13:00:00'),
(254, 51, 31, 14, 'Silicon Valley Innovation', 'Tech support automation and AI', '2024-11-07 09:00:00', '2024-11-07 17:00:00', '2024-11-05 14:45:00', NULL, '2024-11-05 14:45:00'),
(255, 51, 31, 11, 'Sydney Support Center', 'Regional coordination and training', '2024-11-09 08:00:00', '2024-11-09 16:00:00', '2024-11-05 16:20:00', NULL, '2024-11-05 16:20:00');

-- User 32 (SupportTech2 - Jackson Cooper) - Published Journey
INSERT INTO journeys (journey_id, user_id, title, `description`, `start_date`, create_time, update_by, update_time, `status`, `hidden`, cover_image) VALUES
(52, 32, 'Technology Training Expedition', 'Professional development and skill enhancement', '2024-12-01', '2024-12-05 11:25:00', NULL, '2024-12-05 11:25:00', 'public', FALSE, 'uploads/journey/microsoft_certification.jpg');

INSERT INTO events (event_id, journey_id, user_id, location_id, title, `description`, `start_date`, end_date, create_time, update_by, update_time) VALUES
(256, 52, 32, 14, 'Microsoft Certification', 'Azure cloud services training', '2024-12-01 09:00:00', '2024-12-01 17:00:00', '2024-12-05 11:55:00', NULL, '2024-12-05 11:55:00'),
(257, 52, 32, 20, 'Cisco Networking Academy', 'Advanced networking and security', '2024-12-03 08:00:00', '2024-12-03 18:00:00', '2024-12-05 13:40:00', NULL, '2024-12-05 13:40:00'),
(258, 52, 32, 2, 'London Tech Bootcamp', 'Full-stack development intensive', '2024-12-05 09:00:00', '2024-12-05 21:00:00', '2024-12-05 15:15:00', NULL, '2024-12-05 15:15:00'),
(259, 52, 32, 1, 'Auckland Innovation Lab', 'Emerging technologies workshop', '2024-12-07 10:00:00', '2024-12-07 16:00:00', '2024-12-05 17:00:00', NULL, '2024-12-05 17:00:00'),
(260, 52, 32, 13, 'Kuala Lumpur Tech Conference', 'Regional technology trends and AI', '2024-12-09 08:00:00', '2024-12-09 18:00:00', '2024-12-05 18:30:00', NULL, '2024-12-05 18:30:00');

-- User 33 (SupportTech3 - Chloe Barnes) - Published Journey
INSERT INTO journeys (journey_id, user_id, title, `description`, `start_date`, create_time, update_by, update_time, `status`, `hidden`, cover_image) VALUES
(53, 33, 'Customer Success Stories', 'Global user experience research and feedback', '2025-01-10', '2025-01-15 13:50:00', NULL, '2025-01-15 13:50:00', 'public', FALSE, 'uploads/journey/sydney_beta_testing.jpg');

INSERT INTO events (event_id, journey_id, user_id, location_id, title, `description`, `start_date`, end_date, create_time, update_by, update_time) VALUES
(261, 53, 33, 16, 'New York User Conference', 'Customer feedback and product development', '2025-01-10 09:00:00', '2025-01-10 18:00:00', '2025-01-15 14:20:00', NULL, '2025-01-15 14:20:00'),
(262, 53, 33, 6, 'London Focus Groups', 'European user experience research', '2025-01-12 10:00:00', '2025-01-12 16:00:00', '2025-01-15 16:00:00', NULL, '2025-01-15 16:00:00'),
(263, 53, 33, 11, 'Sydney Beta Testing', 'New features testing and validation', '2025-01-14 08:00:00', '2025-01-14 17:00:00', '2025-01-15 17:35:00', NULL, '2025-01-15 17:35:00'),
(264, 53, 33, 3, 'Tokyo Mobile Testing', 'Asian market mobile app optimization', '2025-01-16 09:00:00', '2025-01-16 18:00:00', '2025-01-15 19:15:00', NULL, '2025-01-15 19:15:00'),
(265, 53, 33, 20, 'Toronto Accessibility Review', 'Inclusive design and accessibility standards', '2025-01-18 09:00:00', '2025-01-18 17:00:00', '2025-01-15 20:45:00', NULL, '2025-01-15 20:45:00');

-- User 34 (SupportTech4 - Sebastian Powell) - Published Journey
INSERT INTO journeys (journey_id, user_id, title, `description`, `start_date`, create_time, update_by, update_time, `status`, `hidden`, cover_image) VALUES
(54, 34, 'Quality Assurance Global Tour', 'Software testing methodologies worldwide', '2025-02-05', '2025-02-10 08:30:00', NULL, '2025-02-10 08:30:00', 'public', FALSE, 'uploads/journey/dublin_qa_center.jpg');

INSERT INTO events (event_id, journey_id, user_id, location_id, title, `description`, `start_date`, end_date, create_time, update_by, update_time) VALUES
(266, 54, 34, 5, 'Dublin QA Center', 'Agile testing methodologies and automation', '2025-02-05 09:00:00', '2025-02-05 17:00:00', '2025-02-10 09:00:00', NULL, '2025-02-10 09:00:00'),
(267, 54, 34, 22, 'Ljubljana Testing Lab', 'European quality standards compliance', '2025-02-07 08:00:00', '2025-02-07 16:00:00', '2025-02-10 10:45:00', NULL, '2025-02-10 10:45:00'),
(268, 54, 34, 25, 'Singapore Test Automation', 'AI-powered testing and quality metrics', '2025-02-09 09:00:00', '2025-02-09 18:00:00', '2025-02-10 12:20:00', NULL, '2025-02-10 12:20:00'),
(269, 54, 34, 14, 'San Francisco QA Summit', 'Industry best practices and innovation', '2025-02-11 08:00:00', '2025-02-11 17:00:00', '2025-02-10 14:00:00', NULL, '2025-02-10 14:00:00'),
(270, 54, 34, 1, 'Auckland Performance Testing', 'Load testing and system optimization', '2025-02-13 10:00:00', '2025-02-13 16:00:00', '2025-02-10 15:30:00', NULL, '2025-02-10 15:30:00');

-- User 35 (SupportTech5 - Brian Carter) - Published Journey
INSERT INTO journeys (journey_id, user_id, title, `description`, `start_date`, create_time, update_by, update_time, `status`, `hidden`, cover_image) VALUES
(55, 35, 'IT Infrastructure Exploration', 'Global data centers and network architecture', '2025-03-01', '2025-03-05 12:15:00', NULL, '2025-03-05 12:15:00', 'public', FALSE, 'uploads/journey/london_data_center.jpg');

INSERT INTO events (event_id, journey_id, user_id, location_id, title, `description`, `start_date`, end_date, create_time, update_by, update_time) VALUES
(271, 55, 35, 2, 'London Data Center Tour', 'European server infrastructure and redundancy', '2025-03-01 10:00:00', '2025-03-01 17:00:00', '2025-03-05 12:45:00', NULL, '2025-03-05 12:45:00'),
(272, 55, 35, 16, 'New York Network Hub', 'Fiber optic backbone and connectivity', '2025-03-03 09:00:00', '2025-03-03 18:00:00', '2025-03-05 14:30:00', NULL, '2025-03-05 14:30:00'),
(273, 55, 35, 3, 'Tokyo 5G Implementation', 'Next-generation wireless technology', '2025-03-05 08:00:00', '2025-03-05 16:00:00', '2025-03-05 16:00:00', NULL, '2025-03-05 16:00:00'),
(274, 55, 35, 11, 'Sydney Cloud Operations', 'Multi-cloud deployment strategies', '2025-03-07 09:00:00', '2025-03-07 17:00:00', '2025-03-05 17:45:00', NULL, '2025-03-05 17:45:00'),
(275, 55, 35, 20, 'Vancouver Security Center', 'Cybersecurity monitoring and incident response', '2025-03-09 08:00:00', '2025-03-09 16:00:00', '2025-03-05 19:15:00', NULL, '2025-03-05 19:15:00');

-- For Demo - Advanced Editing
INSERT INTO journeys (journey_id, user_id, title, `description`, `start_date`, create_time, update_by, update_time, `status`, `hidden`, cover_image) VALUES
(56, 3, 'Edit log for free traveller', 'Edit log for free traveller', '2025-06-10', '2025-06-10 08:30:00', NULL, '2025-06-10 08:30:00', 'public', FALSE, NULL),
(57, 13, 'Edit log for premium traveller', 'Edit log for premium traveller', '2025-06-10', '2025-06-10 08:35:00', NULL, '2025-06-10 08:35:00', 'public', FALSE, 'uploads/journey/Camping.jpg'),
(58, 13, 'No Edit for premium traveller', 'No Edit for premium traveller', '2025-06-10', '2025-06-10 08:40:00', NULL, '2025-06-10 08:50:00', 'public', FALSE, NULL);
INSERT INTO events (event_id, journey_id, user_id, location_id, title, `description`, `start_date`, end_date, create_time, update_by, update_time) VALUES
(276, 56, 3, 3, 'Edit log for free traveller - Event', 'Edit log for free traveller - Event', '2025-06-10 09:00:00', '2025-06-10 17:00:00', '2025-06-10 09:00:00', NULL, '2025-06-10 09:00:00');

-- event_images
INSERT INTO event_images (event_id, image_path, upload_time) VALUES
-- Journey 1: European Adventure (User 1)
(1, 'uploads/events/london_bigben.jpg', '2024-06-15 10:00:00'),
(2, 'uploads/events/british_museum.jpg', '2024-06-16 09:00:00'),
(3, 'uploads/events/english_countryside.jpg', '2024-06-18 11:00:00'),
-- Journey 2: Asian Backpacking (User 2)
(6, 'uploads/events/tokyo_street_markets.jpg', '2023-08-16 10:20:00'),
(7, 'uploads/events/kyoto_temples.jpg', '2023-08-17 14:35:00'),
(8, 'uploads/events/great_wall_china.jpg', '2023-08-18 09:50:00'),
-- Journey 3: USA Road Trip (User 3)
(11, 'uploads/events/nyc_start.jpg', '2024-08-10 08:00:00'),
(12, 'uploads/events/chicago_pizza.jpg', '2024-08-12 18:00:00'),
-- Journey 4: Australian Wildlife Adventure (User 4)
(16, 'uploads/events/sydney_prep.jpg', '2023-09-05 12:00:00'),
(17, 'uploads/events/kangaroos.jpg', '2023-09-06 05:00:00'),
(18, 'uploads/events/uluru_sunset.jpg', '2023-09-07 06:00:00'),
-- Journey 5: Mediterranean Cruise (User 5)
(21, 'uploads/events/acropolis_view.jpg', '2024-05-26 10:25:00'),
-- Journey 6: Himalayan Trek (User 6)
(26, 'uploads/events/beijing_preparation.jpg', '2024-09-30 15:30:00'),
(27, 'uploads/events/great_wall_hike.jpg', '2024-10-01 10:20:00'),
(28, 'uploads/events/tibetan_plateau.jpg', '2024-10-03 14:45:00'),
-- Journey 7: South American Tour (User 7)
(31, 'uploads/events/montevideo.jpg', '2024-01-19 09:10:00'),
(32, 'uploads/events/punta_este.jpeg', '2024-01-20 14:30:00'),
-- Journey 8: Antarctic Expedition (User 8)
(36, 'uploads/events/antarctic_ship.jpg', '2024-10-13 10:45:00'),
-- Journey 9: Middle East Discovery (User 9)
(41, 'uploads/events/doha_skyline.jpg', '2024-12-29 09:30:00'),
-- Journey 10: Australian Outback (User 10)
(46, 'uploads/events/sydney_opera.jpg', '2025-01-26 10:20:00'),
-- Journey 11: Nordic Lights Tour (User 11)
(51, 'uploads/events/ljubljana_castle.jpg', '2024-11-18 09:15:00'),
(53, 'uploads/events/postojna_cave.jpg', '2024-11-20 16:45:00'),
-- Journey 12: Japanese Cultural Journey (User 12)
(56, 'uploads/events/tokyo_shibuya.jpg', '2024-04-16 10:20:00'),
(57, 'uploads/events/kyoto_golden_pavilion.jpg', '2024-04-17 14:35:00'),
(58, 'uploads/events/tea_ceremony.jpg', '2024-04-18 11:50:00'),
-- Journey 13: Trans-Siberian Railway (User 13)
(61, 'uploads/events/transsib_train.jpg', '2024-05-02 09:30:00'),
-- Journey 14: Caribbean Vacation (User 14)
(66, 'uploads/events/jamaica_beach.jpg', '2024-06-05 12:30:00'),
-- Journey 15: Alaskan Wilderness (User 15)
(71, 'uploads/events/anchorage_arrival.jpg', '2024-07-20 15:30:00'),
(72, 'uploads/events/denali_national_park.jpg', '2024-07-21 10:20:00'),
(73, 'uploads/events/canadian_rockies.jpg', '2024-07-23 14:45:00'),
-- Journey 16: Middle Earth Tour (User 16)
(76, 'uploads/events/auckland.jpg', '2022-07-20 11:15:00'),
(77, 'uploads/events/hobbiton_set.jpg', '2022-07-22 14:30:00'),
-- Journey 17: Silicon Valley Tech Tour (User 17)
(81, 'uploads/events/san_francisco_tech.jpg', '2024-08-08 09:30:00'),
(82, 'uploads/events/googleplex_campus.jpg', '2024-08-09 14:15:00'),
(83, 'uploads/events/computer_history_museum.jpg', '2024-08-10 11:40:00'),
-- Journey 18: Wine Country Exploration (User 18)
(86, 'uploads/events/english_vineyards.jpg', '2024-10-12 10:20:00'),
(87, 'uploads/events/irish_whiskey.jpg', '2024-10-13 14:35:00'),
(88, 'uploads/events/london_gin.jpg', '2024-10-15 11:50:00'),
-- Journey 19: Arctic Circle Adventure (User 19)
(91, 'uploads/events/yellowknife_aurora.jpg', '2024-10-12 09:30:00'),
-- Journey 20: World War History Tour (User 20)
(96, 'uploads/events/london_war_rooms.jpg', '2025-01-29 10:20:00'),
(97, 'uploads/events/auschwitz_memorial.jpg', '2025-01-30 14:35:00'),
(98, 'uploads/events/imperial_war_museum.jpg', '2025-01-31 11:50:00'),
-- Journey 21: Secret Alpine Retreat (User 11)
(101, 'uploads/events/mountain_cabin.jpg', '2024-03-20 11:00:00'),
(102, 'uploads/events/solo_hiking_trail.jpg', '2024-03-20 12:30:00'),
(103, 'uploads/events/alpine_lake_photography.jpg', '2024-03-20 14:15:00'),
-- Journey 22: Balkans Adventure (User 11)
(106, 'uploads/events/ljubljana_city_tour.jpg', '2024-06-05 10:30:00'),
(106, 'uploads/events/ljubljana_dragon_bridge.jpg', '2024-06-05 11:00:00'),
(106, 'uploads/events/ljubljana_castle_view.jpg', '2024-06-05 12:15:00'),
(106, 'uploads/events/ljubljana_old_town.jpg', '2024-06-05 14:30:00'),
(106, 'uploads/events/ljubljana_river_view.jpg', '2024-06-05 15:45:00'),
(107, 'uploads/events/predjama_castle.jpg', '2024-06-05 12:00:00'),
(108, 'uploads/events/vipava_valley_wine.jpg', '2024-06-05 14:20:00'),
-- Journey 23: Personal Wellness Journey (User 12)
(111, 'uploads/events/ryokan_checkin.jpg', '2024-08-15 15:00:00'),
(112, 'uploads/events/private_onsen.jpg', '2024-08-15 16:30:00'),
(113, 'uploads/events/meditation_garden.jpg', '2024-08-15 18:00:00'),
-- Journey 24: Sakura Season Spectacular (User 12)
(116, 'uploads/events/ueno_park_hanami.jpg', '2024-04-10 12:30:00'),
(116, 'uploads/events/ueno_cherry_blossoms.jpg', '2024-04-10 13:00:00'),
(116, 'uploads/events/ueno_picnic_families.jpg', '2024-04-10 14:30:00'),
(116, 'uploads/events/ueno_pagoda_view.jpg', '2024-04-10 15:45:00'),
(117, 'uploads/events/yoshino_mountain.jpg', '2024-04-10 14:15:00'),
(118, 'uploads/events/philosophers_path.jpg', '2024-04-10 16:00:00'),
-- Journey 25: Solo Siberian Expedition (User 13)
(121, 'uploads/events/remote_cabin_setup.jpg', '2024-09-05 14:00:00'),
(122, 'uploads/events/ice_fishing_siberia.jpg', '2024-09-05 15:30:00'),
(123, 'uploads/events/taiga_forest_trek.jpg', '2024-09-05 17:00:00'),
-- Journey 26: Eastern European Heritage (User 13)
(126, 'uploads/events/moscow_red_square.jpg', '2024-07-25 16:30:00'),
(126, 'uploads/events/moscow_kremlin_walls.jpg', '2024-07-25 17:00:00'),
(126, 'uploads/events/moscow_st_basils.jpg', '2024-07-25 17:45:00'),
(126, 'uploads/events/moscow_gum_store.jpg', '2024-07-25 18:30:00'),
(126, 'uploads/events/moscow_red_square_night.jpg', '2024-07-25 19:15:00'),
(127, 'uploads/events/st_petersburg_palaces.jpg', '2024-07-25 18:00:00'),
(128, 'uploads/events/krakow_old_town.jpg', '2024-07-25 19:30:00'),
-- Journey 27: Family Reunion Planning (User 14)
(131, 'uploads/events/venue_scouting.jpg', '2024-12-20 10:15:00'),
(132, 'uploads/events/catering_arrangements.jpg', '2024-12-20 11:45:00'),
(133, 'uploads/events/accommodation_booking.jpg', '2024-12-20 13:30:00'),
-- Journey 28: Island Hopping Paradise (User 14)
(136, 'uploads/events/barbados_beach_day.jpg', '2024-03-05 13:00:00'),
(136, 'uploads/events/barbados_crystal_waters.jpg', '2024-03-05 13:30:00'),
(136, 'uploads/events/barbados_palm_trees.jpg', '2024-03-05 14:45:00'),
(137, 'uploads/events/blue_mountain_coffee.jpg', '2024-03-05 14:30:00'),
(138, 'uploads/events/fiji_coral_diving.jpg', '2024-03-05 16:00:00'),
-- Journey 29: Personal Photography Project (User 15)
(141, 'uploads/events/equipment_preparation.jpg', '2024-10-05 14:45:00'),
(142, 'uploads/events/golden_hour_shoot.jpg', '2024-10-05 16:15:00'),
(143, 'uploads/events/wildlife_tracking.jpg', '2024-10-05 17:45:00'),
-- Journey 30: American Southwest Road Trip (User 15)
(146, 'uploads/events/antelope_canyon_beams.jpg', '2024-05-20 11:00:00'),
(146, 'uploads/events/antelope_canyon_walls.jpg', '2024-05-20 12:15:00'),
(146, 'uploads/events/antelope_canyon_curves.jpg', '2024-05-20 13:30:00'),
(146, 'uploads/events/antelope_canyon_light_shaft.jpg', '2024-05-20 14:15:00'),
(147, 'uploads/events/monument_valley.jpg', '2024-05-20 12:00:00'),
(148, 'uploads/events/zion_national_park.jpg', '2024-05-20 13:45:00'),
-- Journey 31: Personal Spiritual Journey (User 16)
(151, 'uploads/events/maori_cultural_center.jpg', '2024-02-05 15:50:00'),
(152, 'uploads/events/hot_springs_meditation.jpg', '2024-02-05 17:30:00'),
(153, 'uploads/events/forest_sanctuary.jpg', '2024-02-05 19:00:00'),
-- Journey 32: Kiwi Adventure Sports (User 16)
(156, 'uploads/events/bungee_jumping.jpg', '2024-01-15 12:00:00'),
(156, 'uploads/events/bungee_jumping_bridge.jpg', '2024-01-15 12:30:00'),
(156, 'uploads/events/bungee_jumping_leap.jpg', '2024-01-15 13:15:00'),
(156, 'uploads/events/bungee_jumping_gorge.jpg', '2024-01-15 14:00:00'),
(157, 'uploads/events/white_water_rafting.jpg', '2024-01-15 13:30:00'),
(158, 'uploads/events/skydiving_experience.jpg', '2024-01-15 15:00:00'),
-- Journey 33: Secret Tech Innovation Lab (User 17)
(161, 'uploads/events/lab_setup.jpg', '2024-11-05 17:10:00'),
(162, 'uploads/events/prototype_development.jpg', '2024-11-05 18:45:00'),
(163, 'uploads/events/testing_phase.jpg', '2024-11-05 20:15:00'),
-- Journey 34: West Coast Tech Hubs (User 17)
(166, 'uploads/events/seattle_microsoft_campus.jpg', '2024-08-05 14:00:00'),
(166, 'uploads/events/microsoft_campus_building.jpg', '2024-08-05 14:30:00'),
(166, 'uploads/events/microsoft_visitor_center.jpg', '2024-08-05 15:15:00'),
(166, 'uploads/events/microsoft_innovation.jpg', '2024-08-05 16:00:00'),
(167, 'uploads/events/portland_tech_scene.jpg', '2024-08-05 15:30:00'),
(168, 'uploads/events/silicon_valley_giants.jpg', '2024-08-05 17:00:00'),
-- Journey 35: Culinary Masterclass Retreat (User 18)
(171, 'uploads/events/french_technique_workshop.jpg', '2024-09-20 12:40:00'),
(172, 'uploads/events/michelin_star_experience.jpg', '2024-09-20 14:15:00'),
(173, 'uploads/events/farm_to_table.jpg', '2024-09-20 15:50:00'),
-- Journey 36: British Isles Pub Crawl (User 18)
(176, 'uploads/events/historic_london_pubs.jpg', '2024-06-15 15:00:00'),
(176, 'uploads/events/london_pub_interior.jpg', '2024-06-15 15:30:00'),
(176, 'uploads/events/london_pub_beer.jpg', '2024-06-15 16:15:00'),
(177, 'uploads/events/dublin_traditional_pubs.jpg', '2024-06-15 16:45:00'),
(178, 'uploads/events/edinburgh_whisky_bars.jpg', '2024-06-15 18:20:00'),
-- Journey 37: Personal Fitness Challenge (User 19)
(181, 'uploads/events/base_camp_setup.jpg', '2024-07-05 09:20:00'),
(182, 'uploads/events/high_altitude_training.jpg', '2024-07-05 11:00:00'),
(183, 'uploads/events/endurance_challenge.jpg', '2024-07-05 12:45:00'),
-- Journey 38: Northern Wilderness Adventure (User 19)
(186, 'uploads/events/winter_survival_training.jpg', '2024-01-20 11:15:00'),
(186, 'uploads/events/winter_survival_shelter.jpg', '2024-01-20 11:45:00'),
(186, 'uploads/events/winter_survival_fire.jpg', '2024-01-20 12:30:00'),
(187, 'uploads/events/ice_climbing.jpg', '2024-01-20 12:50:00'),
(188, 'uploads/events/aurora_tracking.jpg', '2024-01-20 14:25:00'),
-- Journey 39: Ancestral Heritage Research
(191, 'uploads/events/genealogy_archives.jpg', '2024-11-15 14:25:00'),
(192, 'uploads/events/irish_parish_records.jpg', '2024-11-15 16:00:00'),
(193, 'uploads/events/highland_clan_history.jpg', '2024-11-15 17:40:00'),
-- Journey 40: European Art Museums Tour (User 20)
(196, 'uploads/events/british_museum_highlights.jpg', '2024-04-25 16:00:00'),
(196, 'uploads/events/british_museum_entrance.jpg', '2024-04-25 16:30:00'),
(196, 'uploads/events/british_museum_great_court.jpg', '2024-04-25 17:00:00'),
(196, 'uploads/events/british_museum_artifacts.jpg', '2024-04-25 17:45:00'),
(197, 'uploads/events/tate_modern_contemporary.jpg', '2024-04-25 17:35:00'),
(198, 'uploads/events/warsaw_national_museum.jpg', '2024-04-25 19:10:00'),
-- Journey 41: Administrative World Tour (User 21)
(201, 'uploads/events/london_business_summit.jpg', '2024-01-10 10:00:00'),
(201, 'uploads/events/london_conference_hall.jpg', '2024-01-10 10:30:00'),
(201, 'uploads/events/london_networking_event.jpg', '2024-01-10 11:15:00'),
(201, 'uploads/events/london_business_district.jpg', '2024-01-10 12:00:00'),
(202, 'uploads/events/singapore_trade_fair.jpg', '2024-01-10 11:30:00'),
(203, 'uploads/events/tokyo_technology_exchange.jpg', '2024-01-10 13:00:00'),
-- Journey 42: Cultural Heritage Expedition (User 22)
(206, 'uploads/events/parthenon_acropolis.jpg', '2024-02-15 14:50:00'),
(206, 'uploads/events/acropolis_columns.jpg', '2024-02-15 15:20:00'),
(206, 'uploads/events/parthenon_restoration.jpg', '2024-02-15 16:00:00'),
(206, 'uploads/events/athens_city_view.jpg', '2024-02-15 16:45:00'),
(207, 'uploads/events/stonehenge_mystery.jpg', '2024-02-15 16:25:00'),
(208, 'uploads/events/auschwitz_memorial_visit.jpg', '2024-02-15 18:00:00'),
-- Journey 43: Strategic Planning Retreat (User 23)
(211, 'uploads/events/ljubljana_innovation_hub.jpg', '2024-03-20 12:15:00'),
(211, 'uploads/events/ljubljana_startup_hub.jpg', '2024-03-20 12:45:00'),
(211, 'uploads/events/ljubljana_innovation_center.jpg', '2024-03-20 13:30:00'),
(211, 'uploads/events/ljubljana_tech_conference.jpg', '2024-03-20 14:15:00'),
(211, 'uploads/events/ljubljana_business_meeting.jpg', '2024-03-20 15:00:00'),
(212, 'uploads/events/silicon_valley_research.jpg', '2024-03-20 13:45:00'),
(213, 'uploads/events/singapore_fintech_summit.jpg', '2024-03-20 15:30:00'),
-- Journey 44: Global Sustainability Initiative (User 24)
(216, 'uploads/events/nz_renewable_energy.jpg', '2024-04-25 13:40:00'),
(216, 'uploads/events/nz_geothermal_plant.jpg', '2024-04-25 14:10:00'),
(216, 'uploads/events/nz_wind_turbines.jpg', '2024-04-25 14:45:00'),
(216, 'uploads/events/nz_solar_installation.jpg', '2024-04-25 15:30:00'),
(217, 'uploads/events/siberian_forest_conservation.jpg', '2024-04-25 15:20:00'),
(218, 'uploads/events/australian_solar_farms.jpg', '2024-04-25 16:55:00'),
-- Journey 45: Digital Transformation Journey (User 25)
(221, 'uploads/events/tokyo_smart_city.jpg', '2024-05-15 16:55:00'),
(221, 'uploads/events/tokyo_smart_building.jpg', '2024-05-15 17:25:00'),
(221, 'uploads/events/tokyo_iot_sensors.jpg', '2024-05-15 18:00:00'),
(221, 'uploads/events/tokyo_ai_center.jpg', '2024-05-15 18:45:00'),
(222, 'uploads/events/edinburgh_data_centers.jpg', '2024-05-15 18:30:00'),
(223, 'uploads/events/dublin_tech_campus.jpg', '2024-05-15 20:00:00'),
-- Journey 46: Literary Landscapes Tour (User 26)
(226, 'uploads/events/shakespeare_country.jpg', '2024-06-05 13:10:00'),
(226, 'uploads/events/stratford_birthplace.jpg', '2024-06-05 13:40:00'),
(226, 'uploads/events/globe_theatre_stage.jpg', '2024-06-05 14:30:00'),
(226, 'uploads/events/shakespeare_memorial.jpg', '2024-06-05 15:15:00'),
(227, 'uploads/events/joyce_dublin_walk.jpg', '2024-06-05 14:45:00'),
(228, 'uploads/events/burns_scotland_heritage.jpg', '2024-06-05 16:20:00'),
-- Journey 47: Art History Masterpiece Tour (User 27)
(231, 'uploads/events/national_gallery_london.jpg', '2024-07-20 15:45:00'),
(231, 'uploads/events/national_gallery_van_gogh.jpg', '2024-07-20 16:15:00'),
(231, 'uploads/events/national_gallery_monet.jpg', '2024-07-20 16:45:00'),
(231, 'uploads/events/national_gallery_turner.jpg', '2024-07-20 17:15:00'),
(231, 'uploads/events/national_gallery_facade.jpg', '2024-07-20 17:45:00'),
(232, 'uploads/events/tate_britain_collection.jpg', '2024-07-20 17:30:00'),
(233, 'uploads/events/ljubljana_modern_gallery.jpg', '2024-07-20 19:00:00'),
-- Journey 48: Documentary Film Locations (User 28)
(236, 'uploads/events/great_barrier_reef_filming.jpg', '2024-08-15 11:00:00'),
(236, 'uploads/events/reef_underwater_camera.jpg', '2024-08-15 11:30:00'),
(236, 'uploads/events/reef_marine_life.jpg', '2024-08-15 12:15:00'),
(236, 'uploads/events/reef_coral_formations.jpg', '2024-08-15 13:00:00'),
(237, 'uploads/events/arctic_wildlife_documentation.jpg', '2024-08-15 12:45:00'),
(238, 'uploads/events/siberian_tiger_reserve.jpg', '2024-08-15 14:20:00'),
-- Journey 49: Historical Battlefields Study (User 29)
(241, 'uploads/events/normandy_dday_beaches.jpg', '2024-09-10 15:20:00'),
(241, 'uploads/events/normandy_omaha_beach.jpg', '2024-09-10 15:50:00'),
(241, 'uploads/events/normandy_memorial.jpg', '2024-09-10 16:30:00'),
(241, 'uploads/events/normandy_bunkers.jpg', '2024-09-10 17:15:00'),
(242, 'uploads/events/westerplatte_memorial.jpg', '2024-09-10 17:00:00'),
(243, 'uploads/events/stalingrad_battlefield.jpg', '2024-09-10 18:35:00'),
-- Journey 50: Fashion Capitals Exploration (User 30)
(246, 'uploads/events/london_fashion_week.jpg', '2024-10-20 17:10:00'),
(246, 'uploads/events/london_fashion_runway.jpg', '2024-10-20 17:40:00'),
(246, 'uploads/events/london_fashion_backstage.jpg', '2024-10-20 18:15:00'),
(246, 'uploads/events/london_fashion_audience.jpg', '2024-10-20 19:45:00'),
(247, 'uploads/events/new_york_fashion_district.jpg', '2024-10-20 18:50:00'),
(248, 'uploads/events/tokyo_harajuku_style.jpg', '2024-10-20 20:25:00'),
-- Journey 51: Technical Support World Tour (User 31)
(251, 'uploads/events/singapore_call_center.jpg', '2024-11-05 09:45:00'),
(251, 'uploads/events/singapore_customer_service.jpg', '2024-11-05 11:00:00'),
(251, 'uploads/events/singapore_support_team.jpg', '2024-11-05 11:45:00'),
(252, 'uploads/events/dublin_tech_support_hub.jpg', '2024-11-05 11:30:00'),
(253, 'uploads/events/tokyo_customer_experience.jpg', '2024-11-05 13:00:00'),
-- Journey 52: Technology Training Expedition (User 32)
(256, 'uploads/events/microsoft_certification.jpg', '2024-12-05 11:55:00'),
(256, 'uploads/events/microsoft_training_room.jpg', '2024-12-05 12:25:00'),
(256, 'uploads/events/microsoft_azure_lab.jpg', '2024-12-05 13:00:00'),
(257, 'uploads/events/cisco_networking_academy.jpg', '2024-12-05 13:40:00'),
(258, 'uploads/events/london_tech_bootcamp.jpg', '2024-12-05 15:15:00'),
-- Journey 53: Customer Success Stories (User 33)
(261, 'uploads/events/ny_conference_networking.jpg', '2025-01-15 15:30:00'),
(261, 'uploads/events/ny_conference_workshops.jpg', '2025-01-15 16:15:00'),
(261, 'uploads/events/ny_conference_exhibition.jpg', '2025-01-15 17:00:00'),
(262, 'uploads/events/london_focus_groups.jpg', '2025-01-15 16:00:00'),
(263, 'uploads/events/sydney_beta_testing.jpg', '2025-01-15 17:35:00'),
-- Journey 54: Quality Assurance Global Tour (User 34)
(266, 'uploads/events/dublin_qa_center.jpg', '2025-02-10 09:00:00'),
(266, 'uploads/events/dublin_qa_testing_lab.jpg', '2025-02-10 09:30:00'),
(266, 'uploads/events/dublin_qa_automation.jpg', '2025-02-10 10:15:00'),
(267, 'uploads/events/ljubljana_testing_lab.jpg', '2025-02-10 10:45:00'),
(268, 'uploads/events/singapore_test_automation.jpg', '2025-02-10 12:20:00'),
-- Journey 55: IT Infrastructure Exploration (User 35)
(271, 'uploads/events/london_data_center.jpg', '2025-03-05 12:45:00'),
(271, 'uploads/events/london_server_racks.jpg', '2025-03-05 13:15:00'),
(271, 'uploads/events/london_cooling_system.jpg', '2025-03-05 13:45:00'),
(271, 'uploads/events/london_network_cables.jpg', '2025-03-05 14:15:00'),
(271, 'uploads/events/london_security_entrance.jpg', '2025-03-05 14:45:00'),
(272, 'uploads/events/new_york_network_hub.jpg', '2025-03-05 14:30:00'),
(273, 'uploads/events/tokyo_5g_implementation.jpg', '2025-03-05 16:00:00');


INSERT INTO announcements (announcement_id, user_id, title, `description`, create_time, update_by, update_time) VALUES
(1, 21, 'Welcome to Our Travel Community!', 'We are excited to have you here. Start sharing your adventures with fellow travelers!', '2024-01-15 09:30:00', NULL, NULL),
(2, 22, 'Scheduled Maintenance Notice', 'The app will be temporarily unavailable this Sunday from 2-4 AM for maintenance.', '2024-01-22 14:15:00', NULL, NULL),
(3, 21, 'Share Your Travel Stories', 'Post your favorite travel moments and inspire others to explore new places.', '2024-02-01 10:00:00', NULL, NULL),
(4, 22, 'Community Guidelines Reminder', 'Please be kind and respectful to all members in our travel community.', '2024-02-10 16:45:00', NULL, NULL),
(5, 21, 'New Update Available', 'Make sure to update to the latest version for the best experience.', '2024-02-18 11:20:00', NULL, NULL),
(6, 22, 'Travel Safety Tips', 'Remember to research local customs and safety information before your trips.', '2024-03-05 13:10:00', NULL, NULL),
(7, 21, 'Photo Contest Coming Soon', 'Stay tuned for details about our upcoming travel photo competition!', '2024-03-10 09:00:00', NULL, NULL),
(8, 22, 'Bug Fixes Implemented', 'We have resolved several reported issues to improve your experience.', '2024-03-22 15:30:00', NULL, NULL),
(9, 21, 'Premium Membership Benefits', 'Discover the advantages of upgrading to a premium account.', '2024-04-02 10:45:00', NULL, NULL),
(10, 22, 'Thank You to Our Users', 'We appreciate you being part of our growing travel community!', '2024-04-15 12:00:00', NULL, NULL);

INSERT INTO achievement_types (`title`, `description`, `points`, `icon_path`, `is_premium`) VALUES
('First Journey', 'Awarded for creating your first journey', 1, 'bi-compass', 0),
('First Event', 'Unlocked when you create your first event', 1, 'bi-geo-alt', 0),
('Going Public', 'Earned by creating your first public journey', 1, 'bi-globe', 0),
('20-Location Explorer', 'Achieved after creating events in 20 different locations', 1, 'bi-geo-fill', 0),
('30-Day Journey', 'Unlocked by creating a journey that lasts at least 30 days', 1, 'bi-infinity', 0),
('Journey Browser', 'Granted after viewing five newly shared journeys', 1, 'bi-eye', 0),
-- ('Map Marker', 'Awarded for adding or editing your first location on the event map', 1, 'bi-map', 0),
-- ('Map Explorer', 'Earned by adding or editing five locations on the event map', 1, 'bi-search', 0),
('First Report', 'Unlocked when you submit your first bug, help, or appeal request', 1, 'bi-bug', 0),
('First Comment', 'Granted after posting your first comment on a bug, help, or appeal request', 1, 'bi-chat-dots', 0),
('5-Report Contributor', 'Earned by submitting at least five bug, help, or appeal requests', 1, 'bi-tools', 0),
('Edit History Viewer', 'Awarded for viewing the complete edit history of your shared journey or event', 1, 'bi-clock-history', 1),
('No-Edit Creator', 'Unlocked when you create your first journey with the "No Edit" flag enabled', 1, 'bi-lock-fill', 1),
('First Follow', 'Earned by following your first shared journey', 1, 'bi-signpost', 1),
('User Follower', 'Awarded for following a user who has shared their journey publicly', 1, 'bi-person-plus', 1),
('Homepage Publisher', 'Unlocked by publishing a journey on the homepage', 1, 'bi-house-door', 1),
('5-Cover Creator', 'Granted after adding a cover image to five different journeys', 1, 'bi-image', 1);

INSERT INTO subscriptions (`subscription_id`, `user_id`, `subscription_type`, `subscription_plan_id`, `start_date`, `expiry_date`,  `created_by`, `note`) VALUES
(1, 16, 'Trial', 1, '2025-06-01', '2025-07-01', NULL, NULL),
(2, 17, 'Trial', 1, '2025-06-01', '2025-07-01', NULL, NULL),
(3, 18, 'Trial', 1, '2025-06-01', '2025-07-01', NULL, NULL),
(4, 19, 'Trial', 1, '2025-06-01', '2025-07-01', NULL, NULL),
(5, 20, 'Trial', 1, '2025-06-01', '2025-07-01', NULL, NULL),
(6, 11, 'Purchased', 2, '2025-06-01', '2025-07-01', NULL, NULL),
(7, 12, 'Purchased', 2, '2025-06-02', '2025-07-02', NULL, NULL),
(8, 13, 'Purchased', 2, '2025-06-03', '2025-07-03', NULL, NULL),
(9, 14, 'Purchased', 2, '2025-06-04', '2025-07-04', NULL, NULL),
(10, 15, 'Purchased', 2, '2025-06-05', '2025-07-05', NULL, NULL),
(11, 37, 'Purchased', 2, '2025-06-05', '2025-07-05', NULL, NULL);

INSERT INTO free_trial_usage (`user_id`, `trial_used`, `subscription_id`) VALUES
(16, 1, 1),
(17, 1, 2),
(18, 1, 3),
(19, 1, 4),
(20, 1, 5);

INSERT INTO payments (`payment_id`, `subscription_id`, `payment_date`, `payment_method`, `payment_amount`, `card_number`, `card_cvv`, `card_expiry_date`, `card_holder`, `card_type`, `billing_country`, `address1`, `city`, `state`, `postal`) VALUES 
(1, 6, '2025-06-01 11:35:02', 'credit_card', '6.00', '1111-1111-1111-1111', '123', '11/2121', 'Benjamin Brooks', 'Visa', 'NZ', '123 Lincoln Road, Lincoln', 'Christchurch', 'Canterbury', '8011'),
(2, 7, '2025-06-02 11:35:02', 'credit_card', '6.00', '1111-1111-1111-1111', '123', '11/2121', 'Harper Gray', 'Mastercard', 'NZ', '123 Lincoln Road, Lincoln', 'Christchurch', 'Canterbury', '8011'),
(3, 8, '2025-06-03 11:35:02', 'credit_card', '6.00', '1111-1111-1111-1111', '123', '11/2121', 'Daniel Reed', 'Visa', 'NZ', '123 Lincoln Road, Lincoln', 'Christchurch', 'Canterbury', '8011'),
(4, 9, '2025-06-04 11:35:02', 'credit_card', '5.22', '1111-1111-1111-1111', '123', '11/2121', 'Evelyn Price', 'Visa', 'OTHERS', '123 Eagle Road,', 'Taipei City', 'Taipei', '101'),
(5, 10, '2025-06-05 11:35:02', 'credit_card', '5.22', '1111-1111-1111-1111', '123', '11/2121', 'Matthew Cox', 'Mastercard', 'OTHERS', '123 Eagle Road,', 'Taipei City', 'Taipei', '101');

-- Achievement Progress 
INSERT INTO achievement_progress (`user_id`, `achievement_type_id`, `current_value`, `target_value`) VALUES 
-- Achievement 1: Trailhead Explorer (first journey)
(1, 1, 1, 1), (2, 1, 1, 1), (3, 1, 1, 1), (4, 1, 1, 1), (5, 1, 1, 1), (6, 1, 1, 1), (7, 1, 1, 1), (8, 1, 1, 1), (9, 1, 1, 1), (10, 1, 1, 1),
(11, 1, 1, 1), (12, 1, 1, 1), (13, 1, 1, 1), (14, 1, 1, 1), (15, 1, 1, 1), (16, 1, 1, 1), (17, 1, 1, 1), (18, 1, 1, 1), (19, 1, 1, 1), (20, 1, 1, 1),
(21, 1, 1, 1), (22, 1, 1, 1), (23, 1, 1, 1), (24, 1, 1, 1), (25, 1, 1, 1), (26, 1, 1, 1), (27, 1, 1, 1), (28, 1, 1, 1), (29, 1, 1, 1), (30, 1, 1, 1),
(31, 1, 1, 1), (32, 1, 1, 1), (33, 1, 1, 1), (34, 1, 1, 1), (35, 1, 1, 1),
-- Achievement 2: Event Initiator (first event)
(1, 2, 1, 1), (2, 2, 1, 1), (3, 2, 1, 1), (4, 2, 1, 1), (5, 2, 1, 1), (6, 2, 1, 1), (7, 2, 1, 1), (8, 2, 1, 1), (9, 2, 1, 1), (10, 2, 1, 1),
(11, 2, 1, 1), (12, 2, 1, 1), (13, 2, 1, 1), (14, 2, 1, 1), (15, 2, 1, 1), (16, 2, 1, 1), (17, 2, 1, 1), (18, 2, 1, 1), (19, 2, 1, 1), (20, 2, 1, 1),
(21, 2, 1, 1), (22, 2, 1, 1), (23, 2, 1, 1), (24, 2, 1, 1), (25, 2, 1, 1), (26, 2, 1, 1), (27, 2, 1, 1), (28, 2, 1, 1), (29, 2, 1, 1), (30, 2, 1, 1),
(31, 2, 1, 1), (32, 2, 1, 1), (33, 2, 1, 1), (34, 2, 1, 1), (35, 2, 1, 1),
-- Achievement 3: Path Shared (first public journey)
(1, 3, 1, 1), (2, 3, 1, 1), (3, 3, 1, 1), (4, 3, 1, 1), (5, 3, 1, 1),
(11, 3, 1, 1), (12, 3, 1, 1), (13, 3, 1, 1), (14, 3, 1, 1), (15, 3, 1, 1), (16, 3, 1, 1), (17, 3, 1, 1), (18, 3, 1, 1), (19, 3, 1, 1), (20, 3, 1, 1),
(21, 3, 1, 1), (22, 3, 1, 1), (23, 3, 1, 1), (24, 3, 1, 1), (25, 3, 1, 1), (26, 3, 1, 1), (27, 3, 1, 1), (28, 3, 1, 1), (29, 3, 1, 1), (30, 3, 1, 1),
(31, 3, 1, 1), (32, 3, 1, 1), (33, 3, 1, 1), (34, 3, 1, 1), (35, 3, 1, 1),
-- Achievement 4: Global Trekker (20 different locations)
(1, 4, 3, 20), (2, 4, 4, 20), (3, 4, 2, 20), (4, 4, 1, 20), (5, 4, 2, 20), (6, 4, 1, 20), (7, 4, 1, 20), (8, 4, 2, 20), (9, 4, 1, 20), (10, 4, 1, 20),
(11, 4, 1, 20), (12, 4, 1, 20), (13, 4, 2, 20), (14, 4, 3, 20), (15, 4, 2, 20), (16, 4, 1, 20), (17, 4, 1, 20), (18, 4, 4, 20), (19, 4, 1, 20), (20, 4, 6, 20),
(21, 4, 5, 20), (22, 4, 5, 20), (23, 4, 5, 20), (24, 4, 5, 20), (25, 4, 5, 20), (26, 4, 4, 20), (27, 4, 5, 20), (28, 4, 5, 20), (29, 4, 4, 20), (30, 4, 5, 20),
(31, 4, 5, 20), (32, 4, 5, 20), (33, 4, 5, 20), (34, 4, 5, 20), (35, 4, 5, 20),
-- Achievement 5: Marathon Voyager (30+ day journey) - All users completed (all journeys are 30+ days old)
(1, 5, 30, 30), (2, 5, 30, 30), (3, 5, 30, 30), (4, 5, 30, 30), (5, 5, 30, 30), (6, 5, 30, 30), (7, 5, 30, 30), (8, 5, 30, 30), (9, 5, 30, 30), (10, 5, 30, 30),
(11, 5, 30, 30), (12, 5, 30, 30), (13, 5, 30, 30), (14, 5, 30, 30), (15, 5, 30, 30), (16, 5, 30, 30), (17, 5, 30, 30), (18, 5, 30, 30), (19, 5, 30, 30), (20, 5, 30, 30),
(21, 5, 30, 30), (22, 5, 30, 30), (23, 5, 30, 30), (24, 5, 30, 30), (25, 5, 30, 30), (26, 5, 30, 30), (27, 5, 30, 30), (28, 5, 30, 30), (29, 5, 30, 30), (30, 5, 30, 30),
(31, 5, 30, 30), (32, 5, 30, 30), (33, 5, 30, 30), (34, 5, 30, 30), (35, 5, 30, 30),
-- Achievement 7: First Bug
(9, 7, 1, 1),(19, 7, 1, 1),(18, 7, 1, 1),
-- Achievement 9: 5 Bugs
(9, 9, 5, 5),(19, 9, 5, 5),(18, 9, 1, 5),
-- Achievement 14: Front Page Adventurer (published journey)
(11, 14, 1, 1), (12, 14, 1, 1), (13, 14, 1, 1), (14, 14, 1, 1), (15, 14, 1, 1), (16, 14, 1, 1), (17, 14, 1, 1), (18, 14, 1, 1), (19, 14, 1, 1), (20, 14, 1, 1),
-- Achievement 15: Visual Voyager (5 cover images) - Premium/Trial users with 1/5 progress
(11, 15, 1, 5), (12, 15, 1, 5), (13, 15, 1, 5), (14, 15, 1, 5), (15, 15, 1, 5), (16, 15, 1, 5), (17, 15, 1, 5), (18, 15, 1, 5), (19, 15, 1, 5), (20, 15, 1, 5);

-- User Achievements (completed achievements only)
INSERT INTO user_achievements (`user_id`, `achievement_type_id`, `unlocked_at`) VALUES
-- Achievement 1: First Journey - Based on journey creation times
(1, 1, '2024-05-10 08:23:45'), (2, 1, '2023-08-15 14:12:33'), (3, 1, '2024-08-05 09:45:21'), 
(4, 1, '2023-06-22 16:30:18'), (5, 1, '2024-05-25 11:20:55'), (6, 1, '2024-09-30 13:15:42'), 
(7, 1, '2024-01-18 10:05:37'), (8, 1, '2024-10-12 15:22:19'), (9, 1, '2024-12-28 12:18:26'), 
(10, 1, '2025-01-25 09:40:13'), (11, 1, '2024-11-17 14:55:48'), (12, 1, '2024-04-15 08:30:22'), 
(13, 1, '2024-05-01 17:12:39'), (14, 1, '2024-06-05 10:25:16'), (15, 1, '2024-07-20 13:45:27'), 
(16, 1, '2022-07-19 11:10:34'), (17, 1, '2024-08-07 15:33:41'), (18, 1, '2024-10-11 09:20:58'), 
(19, 1, '2024-10-11 14:05:12'), (20, 1, '2025-01-28 16:50:29'), (21, 1, '2024-01-10 09:30:00'), 
(22, 1, '2024-02-15 14:20:00'), (23, 1, '2024-03-20 11:45:00'), (24, 1, '2024-04-25 13:10:00'), 
(25, 1, '2024-05-15 16:25:00'), (26, 1, '2024-06-05 12:40:00'), (27, 1, '2024-07-20 15:15:00'), 
(28, 1, '2024-08-15 10:30:00'), (29, 1, '2024-09-10 14:50:00'), (30, 1, '2024-10-20 16:40:00'), 
(31, 1, '2024-11-05 09:15:00'), (32, 1, '2024-12-05 11:25:00'), (33, 1, '2025-01-15 13:50:00'), 
(34, 1, '2025-02-10 08:30:00'), (35, 1, '2025-03-05 12:15:00'),

-- Achievement 2: First Event - Based on first event creation times
(1, 2, '2024-05-11 09:15:00'), (2, 2, '2023-08-16 10:20:00'), (3, 2, '2024-08-05 15:30:00'), 
(4, 2, '2023-06-23 09:30:00'), (5, 2, '2024-05-26 10:25:00'), (6, 2, '2024-09-30 15:30:00'), 
(7, 2, '2024-01-19 09:10:00'), (8, 2, '2024-10-13 10:45:00'), (9, 2, '2024-12-29 09:30:00'), 
(10, 2, '2025-01-26 10:20:00'), (11, 2, '2024-11-18 09:15:00'), (12, 2, '2024-04-16 10:20:00'), 
(13, 2, '2024-05-02 09:30:00'), (14, 2, '2024-06-05 12:30:00'), (15, 2, '2024-07-20 15:30:00'), 
(16, 2, '2022-07-20 11:15:00'), (17, 2, '2024-08-08 09:30:00'), (18, 2, '2024-10-12 10:20:00'), 
(19, 2, '2024-10-12 09:30:00'), (20, 2, '2025-01-29 10:20:00'), (21, 2, '2024-01-10 10:00:00'), 
(22, 2, '2024-02-15 14:50:00'), (23, 2, '2024-03-20 12:15:00'), (24, 2, '2024-04-25 13:40:00'), 
(25, 2, '2024-05-15 16:55:00'), (26, 2, '2024-06-05 13:10:00'), (27, 2, '2024-07-20 15:45:00'), 
(28, 2, '2024-08-15 11:00:00'), (29, 2, '2024-09-10 15:20:00'), (30, 2, '2024-10-20 17:10:00'), 
(31, 2, '2024-11-05 09:45:00'), (32, 2, '2024-12-05 11:55:00'), (33, 2, '2025-01-15 14:20:00'), 
(34, 2, '2025-02-10 09:00:00'), (35, 2, '2025-03-05 12:45:00'),

-- Achievement 3: Going Public (first public journey) - Based on when journeys were made public
(1, 3, '2024-05-10 08:23:45'), (2, 3, '2023-08-15 14:12:33'), (3, 3, '2024-08-05 09:45:21'), 
(4, 3, '2023-06-22 16:30:18'), (5, 3, '2024-05-25 11:20:55'), (11, 3, '2024-11-17 14:55:48'), 
(12, 3, '2024-04-15 08:30:22'), (13, 3, '2024-05-01 17:12:39'), (14, 3, '2024-06-05 10:25:16'), 
(15, 3, '2024-07-20 13:45:27'), (16, 3, '2022-07-19 11:10:34'), (17, 3, '2024-08-07 15:33:41'), 
(18, 3, '2024-10-11 09:20:58'), (19, 3, '2024-10-11 14:05:12'), (20, 3, '2025-01-28 16:50:29'), 
(21, 3, '2024-01-10 09:30:00'), (22, 3, '2024-02-15 14:20:00'), (23, 3, '2024-03-20 11:45:00'), 
(24, 3, '2024-04-25 13:10:00'), (25, 3, '2024-05-15 16:25:00'), (26, 3, '2024-06-05 12:40:00'), 
(27, 3, '2024-07-20 15:15:00'), (28, 3, '2024-08-15 10:30:00'), (29, 3, '2024-09-10 14:50:00'), 
(30, 3, '2024-10-20 16:40:00'), (31, 3, '2024-11-05 09:15:00'), (32, 3, '2024-12-05 11:25:00'), 
(33, 3, '2025-01-15 13:50:00'), (34, 3, '2025-02-10 08:30:00'), (35, 3, '2025-03-05 12:15:00'),

-- Achievement 5: 30-Day Journey - Unlocked 30 days after journey start date
(1, 5, '2024-05-15 08:23:45'), (2, 5, '2023-07-31 14:12:33'), (3, 5, '2024-08-31 09:45:21'), 
(4, 5, '2023-10-05 16:30:18'), (5, 5, '2024-06-19 11:20:55'), (6, 5, '2024-10-21 13:15:42'), 
(7, 5, '2023-12-15 10:05:37'), (8, 5, '2024-12-31 15:22:19'), (9, 5, '2025-01-09 12:18:26'), 
(10, 5, '2023-03-22 09:40:13'), (11, 5, '2024-12-15 14:55:48'), (12, 5, '2024-05-01 08:30:22'), 
(13, 5, '2024-05-31 17:12:39'), (14, 5, '2024-07-05 10:25:16'), (15, 5, '2024-08-19 13:45:27'), 
(16, 5, '2023-07-15 11:10:34'), (17, 5, '2024-07-31 15:33:41'), (18, 5, '2024-11-09 09:20:58'), 
(19, 5, '2024-11-04 14:05:12'), (20, 5, '2025-01-19 16:50:29'), (21, 5, '2024-02-04 09:30:00'), 
(22, 5, '2024-03-11 14:20:00'), (23, 5, '2024-04-14 11:45:00'), (24, 5, '2024-05-20 13:10:00'), 
(25, 5, '2024-06-09 16:25:00'), (26, 5, '2024-07-01 12:40:00'), (27, 5, '2024-08-14 15:15:00'), 
(28, 5, '2024-09-09 10:30:00'), (29, 5, '2024-10-05 14:50:00'), (30, 5, '2024-11-14 16:40:00'), 
(31, 5, '2024-12-01 09:15:00'), (32, 5, '2025-01-04 11:25:00'), (33, 5, '2025-02-09 13:50:00'), 
(34, 5, '2025-03-07 08:30:00'), (35, 5, '2025-04-01 12:15:00'),

-- Achievement 7:
(9, 7, '2024-01-15 11:30:00'), (19, 7, '2024-03-20 11:45:00'), (18, 7, '2025-06-12 16:21:05'), 
-- Achievement 9:
(9, 9, '2025-06-03 12:45:00'), (19, 9, '2025-06-03 14:00:00'),

-- Achievement 14: Homepage Publisher (published journey) - Based on published journey creation times
(11, 14, '2024-06-05 09:15:00'), (12, 14, '2024-04-10 11:45:00'), (13, 14, '2024-07-25 16:00:00'), 
(14, 14, '2024-03-05 12:30:00'), (15, 14, '2024-05-20 10:00:00'), (16, 14, '2024-01-15 11:30:00'), 
(17, 14, '2024-08-05 13:25:00'), (18, 14, '2024-06-15 14:30:00'), (19, 14, '2024-01-20 10:40:00'), 
(20, 14, '2024-04-25 15:30:00');

INSERT INTO support_requests (`request_id`, `user_id`, `issue_type`, `summary`, `description`, `status`, `priority`, `created_at`, `updated_at`) VALUES 
('1', '18', 'Appeal', 'Please restore my sharing permission!', 'Please restore my sharing permission!', 'New', 'High', '2025-06-12 16:21:05', '2025-06-12 16:21:05');
INSERT INTO support_requests (`user_id`, `issue_type`, `summary`, `description`, `screenshot_path`, `status`, `assignee_id`, `priority`, `created_at`)
VALUES 
-- High Priority
(19, 'Bug', 'Critical error on report page', 'Reports fail to generate and show a blank screen.', NULL, 'New', NULL, 'High', '2025-06-01 09:10:00'),
(19, 'Help_Request', 'Need urgent access to admin tools', 'I’ve lost access to essential admin tools and need it restored.', NULL, 'Open', NULL, 'High', '2025-06-02 10:20:00'),
(19, 'Others', 'System timeout during data sync', 'Data sync takes too long and results in a timeout.', NULL, 'Resolved', NULL, 'High', '2025-06-03 14:00:00'),
(19, 'Bug', 'Broken link on main navigation', 'The "Help Center" link leads to a 404 page.', NULL, 'Stalled', NULL, 'High', '2025-06-04 16:35:00'),
(19, 'Others', 'Request for feature clarification', 'Could you please clarify how the new reporting feature works?', NULL, 'Resolved', 28, 'High', '2025-02-09 13:50:00'),
(19, 'Others', 'Suggestion: Add dark mode', 'Dark mode would make it easier to use at night.', NULL, 'Resolved', NULL, 'High', '2024-03-20 11:45:00'),
-- Normal Priority
(9, 'Bug', 'Typo in settings page', 'There is a spelling error in the privacy settings.', NULL, 'Open', NULL, 'Normal', '2025-06-01 08:00:00'),
(9, 'Others', 'Add option to export in XML', 'It would be helpful to export reports in XML format.', NULL, 'New', NULL, 'Normal', '2025-06-02 09:15:00'),
(9, 'Help_Request', 'Clarify usage limits', 'Could you explain the usage limits in the free tier?', NULL, 'Resolved', NULL, 'Normal', '2025-06-03 12:45:00'),
(9, 'Others', 'Profile picture not updating instantly', 'Changes to the profile picture take time to reflect.', NULL, 'Stalled', NULL, 'Normal', '2025-06-04 13:30:00'),
(9, 'Bug', 'Page crashes on submit', 'Submitting the form causes the page to crash with a 500 error.', NULL, 'Resolved', NULL, 'Normal', '2025-01-09 12:18:26'),
(9, 'Help_Request', 'Unable to access dashboard', 'I get a 403 forbidden error when trying to access my dashboard.', NULL, 'Resolved', 25, 'Normal', '2024-01-15 11:30:00')
;