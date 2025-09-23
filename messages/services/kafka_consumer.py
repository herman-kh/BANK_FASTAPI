import asyncio
import json
import logging
from typing import Dict, Any

from aiokafka import AIOKafkaConsumer
from config.config import settings
from services.utils import send_email

logger = logging.getLogger(__name__)


class KafkaConsumerService:
    def __init__(self):
        self.consumer: AIOKafkaConsumer | None = None
        self.running = False

    async def start_consumer(self):
        """Запуск Kafka consumer с автопереподключением"""
        self.running = True

        while self.running:
            try:
                self.consumer = AIOKafkaConsumer(
                    settings.KAFKA_USER_CODE_FOR_REGISTRATION,
                    settings.KAFKA_BILL_EMAIL_TOPIC,
                    settings.KAFKA_MESSAGE_FOR_ALL_USERS,
                    bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
                    group_id=settings.KAFKA_GROUP_ID,
                    auto_offset_reset="earliest",
                    enable_auto_commit=True,
                    value_deserializer=lambda x: json.loads(x.decode("utf-8")),
                )

                await self.consumer.start()
                logger.info(f"Kafka consumer connected to {settings.KAFKA_BOOTSTRAP_SERVERS}")

                async for message in self.consumer:
                    try:
                        if message.topic == settings.KAFKA_USER_CODE_FOR_REGISTRATION:
                            await self.handle_user_code_for_verify_registration_event(message.value)

                        elif message.topic == settings.KAFKA_BILL_EMAIL_TOPIC:
                            await self.handle_bill_message(message.value)

                        elif message.topic == settings.KAFKA_MESSAGE_FOR_ALL_USERS:
                            await self.handle_message_for_all_users(message.value)

                        else:
                            logger.warning(f"Unknown topic {message.topic}, skipping...")

                    except Exception as e:
                        logger.error(f"Error while handling Kafka message: {e}")

            except Exception as e:
                logger.error(f"Kafka connection error: {e}. Reconnecting in 5s...")
                await asyncio.sleep(5)

            finally:
                if self.consumer:
                    await self.consumer.stop()
                    self.consumer = None

    async def stop_consumer(self):
        """Остановка Kafka consumer"""
        self.running = False
        if self.consumer:
            await self.consumer.stop()
            logger.info("Kafka consumer stopped")

    async def handle_user_code_for_verify_registration_event(self, message_data: Dict[str, Any]):
        """Обработка события отправки кода подтверждения"""
        try:
            from_email = settings.FROM_EMAIL
            password = settings.EMAIL_KEY
            user_code = str(message_data.get("code"))
            user_email = message_data.get("email")
            subject = "Verification code for email"

            if not user_email or not user_code:
                logger.error("Invalid message: missing email or code")
                return

            await send_email(subject, user_code, user_email, from_email, password)
            logger.info(f"Sent verification code to {user_email}")

        except Exception as e:
            logger.error(f"Error processing registration event: {e}")

    async def handle_bill_message(self, message_data: Dict[str, Any]):
        """Обработка события с биллом"""
        try:
            from_email = settings.FROM_EMAIL
            password = settings.EMAIL_KEY
            message = str(message_data.get("message"))
            user_email = message_data.get("email")
            subject = "Your bill"

            if not user_email or not message:
                logger.error("Invalid bill message: missing email or text")
                return

            await send_email(subject, message, user_email, from_email, password)
            logger.info(f"Sent bill to {user_email}")

        except Exception as e:
            logger.error(f"Error processing bill message: {e}")

    async def handle_message_for_all_users(self, message_data: Dict[str, Any]):
        try:
            from_email = settings.FROM_EMAIL
            password = settings.EMAIL_KEY
            message = str(message_data.get("message"))
            user_email = message_data.get("email")
            subject = "Message"

            if not user_email or not message:
                logger.error("Invalid message: missing email or text")
                return

            await send_email(subject, message, user_email, from_email, password)
            logger.info(f"Sent message to {user_email}")

        except Exception as e:
            logger.error(f"Error processing message: {e}")


kafka_consumer = KafkaConsumerService()
