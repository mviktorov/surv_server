from pydantic import PostgresDsn
from tortoise import Tortoise

from surv_server.settings import settings

TORTOISE_ORM = {
    "connections": {
        "default": PostgresDsn.build(
            scheme="postgres",
            user=settings.POSTGRES_USER,
            password=settings.POSTGRES_PASSWORD,
            host=settings.POSTGRES_HOST,
            port=str(settings.POSTGRES_PORT),
            path=f"/{settings.POSTGRES_DB_NAME}",
        )
    },
    "apps": {
        "surv_server": {
            "models": [
                "aerich.models",
                "surv_server.tortoise.models"
            ],
            "default_connection": "default",
        },
    },
    "use_tz": True,
}


async def init_db():
    await Tortoise.init(config=TORTOISE_ORM)
