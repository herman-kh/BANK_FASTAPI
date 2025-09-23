from fastapi import FastAPI
import uvicorn
import logging

# from services.kafka_producer import producer
from services.kafka_consumer import kafka_consumer

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI(root_path="/messages")




@app.on_event("startup")
async def startup():
    logger.info("Starting producer and consumer...")
    # await producer.start()
    await kafka_consumer.start_consumer()
    logger.info("Kafka producer and consumer started")


@app.on_event("shutdown")
async def shutdown():
    logger.info("Stopping producer and consumer...")
    # await producer.stop()
    await kafka_consumer.stop_consumer()
    logger.info("Kafka producer and consumer stopped")


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
