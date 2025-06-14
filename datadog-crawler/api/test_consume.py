from fastapi import APIRouter
from confluent_kafka import Consumer
import os
import json

router = APIRouter()

@router.get("/test-consume")
def test_consume_kafka():
    consumer = Consumer({
        'bootstrap.servers': os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092"),
        'group.id': 'summary-consumer',
        'auto.offset.reset': 'earliest',
        'enable.auto.commit': False
    })

    consumer.subscribe(['news_raw'])

    # partition 할당될 때까지 대기
    while not consumer.assignment():
        consumer.poll(0.1)

    msg = consumer.poll(3.0)
    if msg is None:
        return {"message": "⏳ No message available from Kafka"}

    if msg.error():
        return {"error": str(msg.error())}

    try:
        payload = json.loads(msg.value().decode('utf-8'))
        consumer.close()
        return {
            "message": "✅ Successfully consumed 1 item from Kafka!!!!",
            "data": payload
        }
    except Exception as e:
        consumer.close()
        return {"error": f"❗ Failed to parse message: {e}"}
