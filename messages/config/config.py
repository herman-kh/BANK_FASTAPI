import os
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    EMAIL_KEY: str
    TO_EMAIL: str
    FROM_EMAIL : str
    KAFKA_USER_CODE_FOR_REGISTRATION: str
    KAFKA_BILL_EMAIL_TOPIC: str
    KAFKA_BOOTSTRAP_SERVERS: str
    KAFKA_GROUP_ID: str
    KAFKA_MESSAGE_FOR_ALL_USERS: str

    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".env")


    )


settings = Settings()