-- Create users table
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    phone_number VARCHAR(20) NOT NULL,
    location VARCHAR(200) NOT NULL,
    password VARCHAR(255) NOT NULL,
    telegram_chat_id VARCHAR(100),
    telegram_username VARCHAR(100),
    disaster_types TEXT,
    preferred_language VARCHAR(50) DEFAULT 'English',
    is_admin BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
