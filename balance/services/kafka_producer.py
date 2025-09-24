import json
import logging
from aiokafka import AIOKafkaProducer
from config.config import settings
from datetime import datetime
logger = logging.getLogger(__name__)

class KafkaProducer:
    def __init__(self):
        self.producer: AIOKafkaProducer | None = None
        logger.info("KafkaProducer initialized")

    async def start(self):

        try:
            logger.info(f"Starting Kafka Producer...")
            logger.info(f"Connecting to: {settings.KAFKA_BOOTSTRAP_SERVERS}")
            logger.info(f"Target topic: {settings.KAFKA_BILL_EMAIL_TOPIC}")
            
            self.producer = AIOKafkaProducer(
                bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
                value_serializer=lambda v: json.dumps(v).encode("utf-8")
            )
            
            await self.producer.start()
            logger.info("Kafka Producer started successfully")
            logger.info("Successfully connected to Kafka")
            
        except Exception as e:
            logger.error(f"Failed to start Kafka Producer: {e}")
            logger.error("Check if Kafka is running: docker-compose up -d")
            raise

    async def stop(self):
        if self.producer:
            try:
                logger.info("Stopping Kafka Producer...")
                await self.producer.stop()
                logger.info("Kafka Producer stopped successfully")
            except Exception as e:
                logger.error(f"Error while stopping producer: {e}")
        else:
            logger.warning("Producer was not started, nothing to stop")

    async def send_bill_to_user_email(self, email: str, message: str) -> dict:
         if not self.producer:
            logger.error("Producer is not started. Call await producer.start() first")
            raise RuntimeError("Producer is not started")
         
         try:
            event = {
                "email": email,
                "message": message,
                "event_type": "bill_sent",
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
            
            logger.info(f"Preparing to send event for email: {email}")
            logger.debug(f"Event details: {json.dumps(event, indent=2)}")
            
    
            result = await self.producer.send_and_wait(
                settings.KAFKA_BILL_EMAIL_TOPIC, 
                event
            )

            logger.info(f"Successfully sent event for email: {email}")
            logger.info(f"Topic: {result.topic}, Partition: {result.partition}")
            logger.info(f"Offset: {result.offset}")
            
            return {
                "success": True,
                "email": email,
                "message": message,
                "topic": result.topic,
                "partition": result.partition,
                "offset": result.offset
            }
            
         except Exception as e:
            logger.error(f"Failed to send event for email {email}: {e}")
            logger.error("Check topic exists and Kafka is accessible")
            raise
         
        

producer = KafkaProducer()