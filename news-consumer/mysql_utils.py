import mysql.connector
import os
from datetime import datetime
import json

def get_mysql_connection():
    """MySQL 데이터베이스 연결을 반환합니다."""
    try:
        connection = mysql.connector.connect(
            host='mysql-dotnet',
            database='dotnet_sample',
            user='dotnetuser',
            password='dotnetpass',
            port=3306,
            autocommit=True
        )
        return connection
    except mysql.connector.Error as err:
        print(f"❌ MySQL 연결 오류: {err}")
        return None

def create_kafka_test_table():
    """kafka_test_logs 테이블을 생성합니다."""
    connection = get_mysql_connection()
    if connection is None:
        return False
    
    try:
        cursor = connection.cursor()
        
        # 테이블 생성 SQL
        create_table_query = """
        CREATE TABLE IF NOT EXISTS kafka_test_logs (
            id INT AUTO_INCREMENT PRIMARY KEY,
            message_id VARCHAR(50) NOT NULL,
            test_type VARCHAR(100) NOT NULL,
            producer VARCHAR(100) NOT NULL,
            consumer VARCHAR(100) NOT NULL,
            title TEXT NOT NULL,
            source VARCHAR(255) NOT NULL,
            content TEXT,
            test_metadata JSON,
            received_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            INDEX idx_message_id (message_id),
            INDEX idx_test_type (test_type),
            INDEX idx_received_at (received_at)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """
        
        cursor.execute(create_table_query)
        print("✅ kafka_test_logs 테이블이 생성되었습니다.")
        
        cursor.close()
        connection.close()
        return True
        
    except mysql.connector.Error as err:
        print(f"❌ 테이블 생성 오류: {err}")
        if connection:
            connection.close()
        return False

def save_test_message_to_mysql(test_data):
    """테스트 메시지를 MySQL에 저장합니다."""
    connection = get_mysql_connection()
    if connection is None:
        return False
    
    try:
        cursor = connection.cursor()
        
        # 테스트 메타데이터 추출
        test_metadata = test_data.get('test_metadata', {})
        
        insert_query = """
        INSERT INTO kafka_test_logs (
            message_id, test_type, producer, consumer, title, 
            source, content, test_metadata
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        values = (
            test_metadata.get('message_id', 'unknown'),
            test_metadata.get('test_type', 'unknown'),
            test_metadata.get('producer', 'unknown'),
            test_metadata.get('consumer', 'unknown'),
            test_data.get('title', ''),
            test_data.get('source', ''),
            test_data.get('content', ''),
            json.dumps(test_metadata)
        )
        
        cursor.execute(insert_query, values)
        record_id = cursor.lastrowid
        
        print(f"✅ 테스트 메시지가 MySQL에 저장되었습니다. ID: {record_id}")
        print(f"   Message: {test_data.get('title', 'No title')}")
        
        cursor.close()
        connection.close()
        return True
        
    except mysql.connector.Error as err:
        print(f"❌ MySQL 저장 오류: {err}")
        if connection:
            connection.close()
        return False

def get_test_message_count():
    """저장된 테스트 메시지 개수를 반환합니다."""
    connection = get_mysql_connection()
    if connection is None:
        return 0
    
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM kafka_test_logs")
        count = cursor.fetchone()[0]
        
        cursor.close()
        connection.close()
        return count
        
    except mysql.connector.Error as err:
        print(f"❌ MySQL 카운트 조회 오류: {err}")
        if connection:
            connection.close()
        return 0