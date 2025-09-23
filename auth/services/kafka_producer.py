import json
import logging
from datetime import datetime
from aiokafka import AIOKafkaProducer
from config.config import settings

logger = logging.getLogger(__name__)

class KafkaProducer:
    def __init__(self):
        self.producer: AIOKafkaProducer | None = None
        logger.info("KafkaProducer initialized")

    async def start(self):
        """Запуск продюсера с подробным логированием"""
        try:
            logger.info(f"Starting Kafka Producer...")
            logger.info(f"Connecting to: {settings.KAFKA_BOOTSTRAP_SERVERS}")
            logger.info(f"Available topics: {settings.KAFKA_USER_CREATED_TOPIC}, {settings.KAFKA_USER_CODE_FOR_REGISTRATION}, {settings.KAFKA_MESSAGE_FOR_ALL_USERS}")
            
            self.producer = AIOKafkaProducer(
                bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
                value_serializer=lambda v: json.dumps(v).encode("utf-8"),
                acks="all",  # Гарантированная доставка
                retry_backoff_ms=500,  # Повторные попытки при ошибках
                enable_idempotence=True  # Гарантия exactly-once доставки
            )
            
            await self.producer.start()
            logger.info("Kafka Producer started successfully")
            logger.info("Successfully connected to Kafka")
            
        except Exception as e:
            logger.error(f"Failed to start Kafka Producer: {e}")
            logger.error("Check if Kafka is running: docker-compose up -d")
            logger.error(f"Check bootstrap servers: {settings.KAFKA_BOOTSTRAP_SERVERS}")
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

    async def send_user_created(self, user_id: int, email: str):
        """Отправка события создания пользователя"""
        if not self.producer:
            logger.error("Producer is not started. Call await producer.start() first")
            raise RuntimeError("Producer is not started")
        
        try:
            event = {
                "user_id": user_id,
                "email": email,
                "event_type": "user_created",
                "timestamp": datetime.utcnow().isoformat() + "Z" 
            }
            
            logger.info(f"Preparing to send user_created event for user_id: {user_id}")
            logger.info(event)
            logger.debug(f"Event details: {json.dumps(event, indent=2)}")
            
            # Отправляем сообщение в правильный топик
            result = await self.producer.send_and_wait(
                settings.KAFKA_USER_CREATED_TOPIC, 
                event
            )
            
            # Логируем детали отправки
            logger.info(f"Successfully sent user_created event for user_id: {user_id}")
            logger.info(f"Topic: {result.topic}, Partition: {result.partition}")
            logger.info(f"Offset: {result.offset}")
            
            return {
                "success": True,
                "user_id": user_id,
                "email": email,
                "topic": result.topic,
                "partition": result.partition,
                "offset": result.offset
            }
            
        except Exception as e:
            logger.error(f"Failed to send user_created event for user_id {user_id}: {e}")
            logger.error("Check if topic exists and Kafka is accessible")
            raise

    async def send_registration_verify_message(self, code: int, email: str):
        """Отправка кода подтверждения регистрации"""
        if not self.producer:
            logger.error("Producer is not started. Call await producer.start() first")
            raise RuntimeError("Producer is not started")
        
        try:
            event = {
                "code": code,
                "email": email,
                "event_type": "code_sent",
                "timestamp": datetime.utcnow().isoformat() + "Z"  # Текущее время
            }
            
            logger.info(f"Preparing to send verification code for email: {email}")
            logger.debug(f"Event details: {json.dumps(event, indent=2)}")
            
            result = await self.producer.send_and_wait(
                settings.KAFKA_USER_CODE_FOR_REGISTRATION, 
                event
            )
            
            logger.info(f"Successfully sent verification code {code} to email: {email}")
            logger.info(f"Topic: {result.topic}, Partition: {result.partition}")
            logger.info(f"Offset: {result.offset}")

            return {
                "success": True,
                "email": email,
                "code": code,
                "topic": result.topic,
                "partition": result.partition,
                "offset": result.offset
            }
            
        except Exception as e:
            logger.error(f"Failed to send verification code to {email}: {e}")
            logger.error("Check if topic exists and Kafka is accessible")
            # Можно добавить повторную попытку или отложенную отправку
            raise

    async def send_message_to_all_users(self, emails: list[str], message: str) -> dict:
         if not self.producer:
            logger.error("Producer is not started. Call await producer.start() first")
            raise RuntimeError("Producer is not started")
         
         try:
            for email in emails:
                event = {
                "email": email,
                "message": message,
                "event_type": "message_for_all_users",
                "timestamp": datetime.utcnow().isoformat() + "Z"
                 }
            
                logger.info(f"Preparing to send event for email: {email}")
                logger.debug(f"Event details: {json.dumps(event, indent=2)}")
            
            # Отправляем сообщение
                result = await self.producer.send_and_wait(
                    settings.KAFKA_MESSAGE_FOR_ALL_USERS, 
                    event
                )
            
            # Логируем детали отправки
                logger.info(f"Successfully sent event for email: {email}")
                logger.info(f"Topic: {result.topic}, Partition: {result.partition}")
                logger.info(f"Offset: {result.offset}")
                
            return {
                    "success": True,
                    "message": message,
                    "topic": result.topic,
                    "partition": result.partition,
                    "offset": result.offset
                }
            
         except Exception as e:
            logger.error(f"Failed to send event for email {email}: {e}")
            logger.error("Check topic exists and Kafka is accessible")
            raise

# Глобальный инстанс продюсера
producer = KafkaProducer()