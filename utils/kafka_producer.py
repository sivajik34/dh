# ============================================================================
# KAFKA INTEGRATION (utils/kafka_producer.py)
# ============================================================================
from kafka import KafkaProducer
import json

class EventProducer:
    def __init__(self, bootstrap_servers=['kafka:9092']):
        self.producer = KafkaProducer(
            bootstrap_servers=bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
    
    def send_event(self, topic: str, event: dict):
        self.producer.send(topic, value=event)
        self.producer.flush()
    
    def send_escalation(self, escalation_data: dict):
        self.send_event('escalation_queue', escalation_data)
    
    def send_audit_log(self, log_data: dict):
        self.send_event('audit_logs', log_data)
    
    def send_feedback(self, feedback_data: dict):
        self.send_event('user_feedback', feedback_data)