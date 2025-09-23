import asyncio
import json
import logging
from typing import Dict, Any

from aiokafka import AIOKafkaConsumer

from config.config import settings
from data.database import AsyncSessionLocal
from .crud import UserService

logger = logging.getLogger(__name__)

class KafkaConsumerService:
    def __init__(self):
        self.consumer: AIOKafkaConsumer | None = None
        self.running = False

    async def start_consumer(self):
        """Запуск Kafka consumer с автопереподключением"""
        max_retries = 10
        retry_delay = 5

        for attempt in range(max_retries):
            try:
                self.consumer = AIOKafkaConsumer(
                    settings.KAFKA_USER_CREATED_TOPIC,
                    bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
                    group_id=settings.KAFKA_GROUP_ID,
                    auto_offset_reset='earliest',
                    enable_auto_commit=True,
                    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
                )

                await self.consumer.start()
                self.running = True
                logger.info("Kafka consumer started successfully")

                try:
                    async for message in self.consumer:
                        await self.handle_user_created_event(message.value)
                except Exception as e:
                    logger.error(f"Error in Kafka consumer loop: {e}")
                finally:
                    await self.consumer.stop()
                    logger.info("Kafka consumer stopped")
                return

            except Exception as e:
                logger.error(f"Failed to start Kafka consumer (attempt {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    logger.info(f"Retrying in {retry_delay} seconds...")
                    await asyncio.sleep(retry_delay)
                else:
                    logger.error("Failed to start Kafka consumer after all attempts")
                    break

    async def handle_user_created_event(self, message_data: Dict[str, Any]):
        """Обработка события создания пользователя"""
        try:
            user_id = message_data.get('user_id')
            email=message_data.get('email')
            logger.info(user_id)
            logger.info(email)
            if not user_id:
                logger.error("Missing user_id in message")
                return
            if not email:
                logger.error("Missing email in message")
                return

            async with AsyncSessionLocal() as db:
                user_service = UserService(db)
                await user_service.create_user(user_id)
                logger.info(f"Created user profile for user_id: {user_id}")
                await db.commit()
                await user_service.create_id_and_email_note(user_id, email)
                logger.info(f"Created user profile for user_id: {user_id} and {email}")
                await db.commit()
                logger.info(f"Email successfully added {email}")
        except Exception as e:
            logger.error(f"Error: {e}")

    async def stop_consumer(self):
        self.running = False
        if self.consumer:
            await self.consumer.stop()
            logger.info("Kafka consumer stopped via stop()")


kafka_consumer = KafkaConsumerService()
