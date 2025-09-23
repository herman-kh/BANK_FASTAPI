import os
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    DATABASE_URL: str
    SECRET_kEY: str
    JWT_ALGHORITM: str
    JSON_FILE: str
    JSON_FILE2: str
    SECRET: str

    KAFKA_BOOTSTRAP_SERVERS : str
    KAFKA_USER_CREATED_TOPIC: str
    KAFKA_GROUP_ID: str
    KAFKA_BILL_EMAIL_TOPIC: str

    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".env")


    )


settings = Settings()