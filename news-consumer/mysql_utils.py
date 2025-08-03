"""
MySQL 연결 및 테스트 데이터 관리 유틸리티
"""
import mysql.connector
import os
from typing import Optional
import json
from datetime import datetime

def get_mysql_connection():
    """MySQL 데이터베이스 연결을 생성합니다."""
    try:
        connection = mysql.connector.connect(
            host='mysql',  # Docker Compose 서비스명
            database='dotnet_sample',
            user='root',
            password='password',
            charset='utf8mb4',
            autocommit=True
        )
        return connection
    except mysql.connector.Error as e:
        print(f"❌ MySQL connection error: {e}")
        return None

def create_kafka_test_table():
    """테스트 로그 테이블을 생성합니다."""
    connection = get_mysql_connection()
    if connection is None:
        return False
    
    try:
        cursor = connection.cursor()
        
        # 테스트 테이블 생성
        create_table_query = """
        CREATE TABLE IF NOT EXISTS kafka_test_logs (
            id INT AUTO_INCREMENT PRIMARY KEY,
            message_id VARCHAR(255) NOT NULL,
            title VARCHAR(500) NOT NULL,
            source VARCHAR(255) NOT NULL,
            content TEXT,
            received_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            test_metadata JSON,
            INDEX idx_message_id (message_id),
            INDEX idx_received_at (received_at)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """
        
        cursor.execute(create_table_query)
        cursor.close()
        connection.close()
        
        print("✅ kafka_test_logs 테이블이 준비되었습니다.")
        return True
        
    except mysql.connector.Error as e:
        print(f"❌ Table creation error: {e}")
        return False

def save_test_message_to_mysql(message_data: dict):
    """테스트 메시지를 MySQL에 저장합니다."""
    connection = get_mysql_connection()
    if connection is None:
        return False
    
    try:
        cursor = connection.cursor()
        
        # 테스트 메시지인지 확인
        if 'test_metadata' not in message_data:
            return False
        
        insert_query = """
        INSERT INTO kafka_test_logs (message_id, title, source, content, test_metadata)
        VALUES (%s, %s, %s, %s, %s)
        """
        
        values = (
            message_data.get('_id', ''),
            message_data.get('title', ''),
            message_data.get('source', ''),
            message_data.get('content', ''),
            json.dumps(message_data.get('test_metadata', {}))
        )
        
        cursor.execute(insert_query, values)
        cursor.close()
        connection.close()
        
        print(f"✅ 테스트 메시지 저장됨: {message_data.get('title', 'Unknown')}")
        return True
        
    except mysql.connector.Error as e:
        print(f"❌ Save test message error: {e}")
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
        
    except mysql.connector.Error as e:
        print(f"❌ Get test message count error: {e}")
        return 0

def get_latest_test_messages(limit: int = 10):
    """최근 테스트 메시지들을 반환합니다."""
    connection = get_mysql_connection()
    if connection is None:
        return []
    
    try:
        cursor = connection.cursor()
        
        query = """
        SELECT message_id, title, source, content, received_at, test_metadata
        FROM kafka_test_logs 
        ORDER BY received_at DESC 
        LIMIT %s
        """
        
        cursor.execute(query, (limit,))
        results = []
        
        for row in cursor.fetchall():
            results.append({
                'message_id': row[0],
                'title': row[1],
                'source': row[2],
                'content': row[3],
                'received_at': row[4].isoformat() if row[4] else None,
                'test_metadata': json.loads(row[5]) if row[5] else {}
            })
        
        cursor.close()
        connection.close()
        return results
        
    except mysql.connector.Error as e:
        print(f"❌ Get latest test messages error: {e}")
        return []

# 모듈 초기화 시 테이블 생성
if __name__ != "__main__":
    create_kafka_test_table()