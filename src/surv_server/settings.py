import os

from pydantic import BaseSettings

env_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))


class VideoServerSettings(BaseSettings):
    FTP_BIND_HOST: str = "0.0.0.0"
    FTP_BIND_PORT: int = 2121
    FTP_UPLOAD_USER: str = "videosrv"
    FTP_UPLOAD_PASSWORD: str
    FTP_UPLOAD_PERMISSIONS: str = "eamw"

    DATA_DIR: str = "./data"

    TELEGRAM_BOT_TOKEN: str
    TELEGRAM_BOT_ADMIN: str

    class Config:
        env_prefix = "SURV_SERVER_"


settings = VideoServerSettings(
    _env_file=os.getenv("CONFIG_FILE_PATH", default=os.path.join(env_path, ".env"))
)
