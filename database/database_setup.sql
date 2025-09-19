-- MoMo SMS Database - phpMyAdmin Compatible Version
CREATE DATABASE IF NOT EXISTS momo_sms_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE momo_sms_db;


-- Drop existing tables
SET FOREIGN_KEY_CHECKS = 0;
DROP TABLE IF EXISTS user_relationships;
DROP TABLE IF EXISTS system_logs;
DROP TABLE IF EXISTS transactions;
DROP TABLE IF EXISTS transaction_categories;
DROP TABLE IF EXISTS users;
SET FOREIGN_KEY_CHECKS = 1;


-- Users Table
CREATE TABLE users (
   user_id INT AUTO_INCREMENT PRIMARY KEY,
   full_name VARCHAR(100) NOT NULL,
   phone_number VARCHAR(15) UNIQUE NOT NULL,
   account_status ENUM('active', 'inactive', 'suspended') DEFAULT 'active',
   created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
   updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB;


-- Transaction Categories Table
CREATE TABLE transaction_categories (
   category_id INT AUTO_INCREMENT PRIMARY KEY,
   category_name VARCHAR(50) NOT NULL UNIQUE,
   category_code VARCHAR(10) NOT NULL UNIQUE,
   description TEXT,
   is_active BOOLEAN DEFAULT TRUE,
   created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
   updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB;


-- Transactions Table
CREATE TABLE transactions (
   transaction_id BIGINT AUTO_INCREMENT PRIMARY KEY,
   financial_transaction_id VARCHAR(20) UNIQUE,
   sender_user_id INT,
   receiver_user_id INT,
   category_id INT NOT NULL,
   amount DECIMAL(15,2) NOT NULL,
   currency VARCHAR(3) DEFAULT 'RWF',
   fee DECIMAL(10,2) DEFAULT 0.00,
   new_balance DECIMAL(15,2),
   transaction_datetime DATETIME NOT NULL,
   status ENUM('completed', 'pending', 'failed') DEFAULT 'completed',
   message_content TEXT,
   sender_message TEXT,
   created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  
   FOREIGN KEY (sender_user_id) REFERENCES users(user_id) ON DELETE SET NULL ON UPDATE CASCADE,
   FOREIGN KEY (receiver_user_id) REFERENCES users(user_id) ON DELETE SET NULL ON UPDATE CASCADE,
   FOREIGN KEY (category_id) REFERENCES transaction_categories(category_id) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB;


-- System Logs Table
CREATE TABLE system_logs (
   log_id BIGINT AUTO_INCREMENT PRIMARY KEY,
   transaction_id BIGINT,
   operation_type ENUM('insert', 'update', 'delete', 'error') NOT NULL,
   operation_status ENUM('success', 'failure', 'pending') NOT NULL,
   error_message TEXT,
   processed_by VARCHAR(100),
   processing_time DECIMAL(8,3) DEFAULT 0.000,
   created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  
   FOREIGN KEY (transaction_id) REFERENCES transactions(transaction_id) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;


-- User Relationships Table
CREATE TABLE user_relationships (
   relationship_id INT AUTO_INCREMENT PRIMARY KEY,
   user1_id INT NOT NULL,
   user2_id INT NOT NULL,
   relationship_type ENUM('frequent_sender', 'frequent_receiver', 'family', 'business') NOT NULL,
   transaction_count INT DEFAULT 0,
   total_amount DECIMAL(15,2) DEFAULT 0.00,
   created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
   last_transaction_date DATETIME,
  
   FOREIGN KEY (user1_id) REFERENCES users(user_id) ON DELETE CASCADE ON UPDATE CASCADE,
   FOREIGN KEY (user2_id) REFERENCES users(user_id) ON DELETE CASCADE ON UPDATE CASCADE,
   UNIQUE KEY unique_user_relationship (user1_id, user2_id)
) ENGINE=InnoDB;


-- Create Indexes
CREATE INDEX idx_transactions_datetime ON transactions(transaction_datetime);
CREATE INDEX idx_transactions_sender ON transactions(sender_user_id);
CREATE INDEX idx_transactions_receiver ON transactions(receiver_user_id);
CREATE INDEX idx_transactions_category ON transactions(category_id);
CREATE INDEX idx_transactions_fin_id ON transactions(financial_transaction_id);
CREATE INDEX idx_users_phone ON users(phone_number);
CREATE INDEX idx_transactions_user_date ON transactions(sender_user_id, transaction_datetime);
CREATE INDEX idx_transactions_category_date ON transactions(category_id, transaction_datetime);


-- Insert Sample Data
INSERT INTO transaction_categories (category_name, category_code, description, is_active) VALUES
('Money Transfer', 'TRANSFER', 'Direct money transfers between users', TRUE),
('Money Received', 'RECEIVED', 'Money received from other users or external sources', TRUE),
('Bank Deposit', 'DEPOSIT', 'Bank deposits to mobile money account', TRUE),
('Payment Service', 'PAYMENT', 'Payments to merchants and service providers', TRUE),
('Airtime Purchase', 'AIRTIME', 'Mobile airtime and data bundle purchases', TRUE),
('Direct Payment', 'DIRECT_PAY', 'Direct payments by external entities', TRUE);


INSERT INTO users (full_name, phone_number, account_status) VALUES
('Jane Smith', '250791666666', 'active'),
('Samuel Carter', '250790777777', 'active'),
('Alex Doe', '250791666667', 'active'),
('Robert Brown', '250788999999', 'active'),
('Linda Green', '250789888888', 'active'),
('Account Holder', '250795963036', 'active');


INSERT INTO transactions (financial_transaction_id, sender_user_id, receiver_user_id, category_id, amount, fee, new_balance, transaction_datetime, message_content) VALUES
('76662021700', 1, 6, 2, 2000.00, 0.00, 2000.00, '2024-05-10 16:30:51', 'You have received 2000 RWF from Jane Smith'),
('73214484437', 6, 1, 4, 1000.00, 0.00, 1000.00, '2024-05-10 16:31:39', 'Your payment of 1,000 RWF to Jane Smith has been completed'),
('CASH001', 6, 6, 3, 40000.00, 0.00, 40400.00, '2024-05-11 18:43:49', 'A bank deposit of 40000 RWF has been added to your account'),
('TRANSFER001', 6, 2, 1, 10000.00, 100.00, 28300.00, '2024-05-11 20:34:47', '10000 RWF transferred to Samuel Carter'),
('13913173274', 6, NULL, 5, 2000.00, 0.00, 25280.00, '2024-05-12 11:41:28', 'Your payment of 2000 RWF to Airtime completed');


INSERT INTO user_relationships (user1_id, user2_id, relationship_type, transaction_count, total_amount, last_transaction_date) VALUES
(6, 1, 'frequent_receiver', 2, 1000.00, '2024-05-10 16:31:39'),
(6, 2, 'frequent_sender', 1, 10000.00, '2024-05-11 20:34:47'),
(1, 6, 'frequent_sender', 1, 2000.00, '2024-05-10 16:30:51');


INSERT INTO system_logs (transaction_id, operation_type, operation_status, processed_by, processing_time) VALUES
(1, 'insert', 'success', 'SMS_PROCESSOR_v1.0', 0.125),
(2, 'insert', 'success', 'SMS_PROCESSOR_v1.0', 0.098),
(3, 'insert', 'success', 'SMS_PROCESSOR_v1.0', 0.156),
(4, 'insert', 'success', 'SMS_PROCESSOR_v1.0', 0.134),
(5, 'insert', 'success', 'SMS_PROCESSOR_v1.0', 0.089);



