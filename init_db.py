import os
import pymysql
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def init_db():
    try:
        # Connect to MySQL server (without specifying database)
        connection = pymysql.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            user=os.getenv('DB_USER', 'root'),
            password=os.getenv('DB_PASSWORD', 'root'),
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )

        with connection.cursor() as cursor:
            # Create database if it doesn't exist
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {os.getenv('DB_NAME', 'rakshasetu')}")
            cursor.execute(f"USE {os.getenv('DB_NAME', 'rakshasetu')}")
            
            # Create users table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    full_name VARCHAR(255) NOT NULL,
                    phone_number VARCHAR(20) NOT NULL,
                    email VARCHAR(255) NOT NULL,
                    address TEXT NOT NULL,
                    region VARCHAR(255) NOT NULL,
                    disaster_types TEXT NOT NULL,
                    preferred_language VARCHAR(50) NOT NULL,
                    communication_channel VARCHAR(50) NOT NULL,
                    telegram_username VARCHAR(255),
                    internet_access VARCHAR(10) NOT NULL,
                    special_needs TEXT,
                    first_aid_trained VARCHAR(5) NOT NULL,
                    disaster_education VARCHAR(5) NOT NULL,
                    emergency_contact_name VARCHAR(255) NOT NULL,
                    emergency_contact_phone VARCHAR(20) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    INDEX idx_region (region),
                    INDEX idx_telegram (telegram_username)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """)

            # Create alerts table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS alerts (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    type VARCHAR(50) NOT NULL,
                    region VARCHAR(255) NOT NULL,
                    message TEXT NOT NULL,
                    severity VARCHAR(20) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    INDEX idx_type_region (type, region),
                    INDEX idx_created_at (created_at)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """)
            
            connection.commit()
            print("Database and tables created successfully!")

    except Exception as e:
        print(f"Error initializing database: {str(e)}")
    finally:
        connection.close()

if __name__ == '__main__':
    init_db()
