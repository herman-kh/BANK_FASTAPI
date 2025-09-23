from fastapi import FastAPI
import web.router, web.admin_router
from services.kafka_consumer import kafka_consumer
from services.kafka_producer import producer
import asyncio
import logging
from contextlib import asynccontextmanager

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI(root_path="/balance")

app.include_router(web.router.router)
app.include_router(web.admin_router.router)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Kafka producer and consumer in background...")
    
    # Запускаем продюсер и консьюмер в фоне
    consumer_task = asyncio.create_task(kafka_consumer.start_consumer())
    producer_task = asyncio.create_task(producer.start())

    # Ждём небольшую паузу, чтобы uvicorn открыл порт
    await asyncio.sleep(0.1)
    
    try:
        yield
    finally:
        logger.info("Stopping Kafka producer and consumer...")
        # Корректно останавливаем
        await kafka_consumer.stop_consumer()
        await producer.stop()
        # Отменяем задачи на случай, если они еще живы
        consumer_task.cancel()
        producer_task.cancel()
        logger.info("Kafka producer and consumer stopped.")

app.router.lifespan_context = lifespan

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
