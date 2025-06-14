from confluent_kafka import Producer
import os
import json

bootstrap_servers = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
producer = Producer({'bootstrap.servers': bootstrap_servers})

def send_news_to_kafka(news_item: dict):
    producer.produce(
        topic='news_raw',
        value=json.dumps(news_item).encode('utf-8'),
        callback=lambda err, msg: print(
            f"✅ Sent to Kafka: {msg.key() or ''}" if not err else f"❌ Kafka error: {err}"
        )
    )
    producer.flush()