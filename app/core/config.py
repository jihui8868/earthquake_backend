from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "Earthquake Backend"
    DEBUG: bool = False

    DATABASE_HOST: str = "192.168.2.133"
    DATABASE_PORT: int = 5432
    DATABASE_USER: str = "postgres"
    DATABASE_PASSWORD: str = "111111"
    DATABASE_NAME: str = "earthquake"

    UPLOAD_DIR: str = "uploads"

    MINIO_ENDPOINT: str = "192.168.2.133:9000"
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = "minioadmin"
    MINIO_SECURE: bool = False
    MINIO_BUCKET: str = "earthquake"

    @property
    def DATABASE_URL(self) -> str:
        return (
            f"postgresql+asyncpg://{self.DATABASE_USER}:{self.DATABASE_PASSWORD}@{self.DATABASE_HOST}:{self.DATABASE_PORT}/{self.DATABASE_NAME}"
        )

    model_config = {"env_file": ".env"}


settings = Settings()
