import os

from pydantic import BaseSettings

env_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))


class VideoServerSettings(BaseSettings):
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_DB_NAME: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str

    FN_REGEXP_TO_CAMERA: str

    FTP_BIND_HOST: str = "0.0.0.0"
    FTP_BIND_PORT: int = 2121
    FTP_UPLOAD_USER: str = "videosrv"
    FTP_UPLOAD_PASSWORD: str
    FTP_UPLOAD_PERMISSIONS: str = "eamw"
    FTP_PASSIVE_PORTS_FROM: int = 60000
    FTP_PASSIVE_PORTS_TO: int = 65535
    FTP_LOG_LEVEL: str = "INFO"
    FTP_NAT_ADDRESS: str | None = None

    DATA_DIR: str = "./data"

    TELEGRAM_PHOTO_EXTENSIONS_TO_SEND_CSV: str = "jpg"

    TELEGRAM_BOT_TOKEN: str
    TELEGRAM_BOT_ADMIN: str

    class Config:
        env_prefix = "SURV_SERVER_"


settings = VideoServerSettings(
    _env_file=os.getenv("CONFIG_FILE_PATH", default=os.path.join(env_path, ".env"))
)
