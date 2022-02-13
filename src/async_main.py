import asyncio
import logging
import os

import aioftp
from tortoise import Tortoise

from surv_server.ftp.ftp_server import SurvFTPServer
from surv_server.settings import settings
from surv_server.tortoise.db import TORTOISE_ORM

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.DEBUG
)
logging.root.setLevel(logging.DEBUG)


async def main():
    ftp_upload_dir = os.path.join(settings.DATA_DIR, "ftp")
    os.makedirs(ftp_upload_dir, exist_ok=True)

    users = (
        aioftp.User(
            login=settings.FTP_UPLOAD_USER,
            password=settings.FTP_UPLOAD_PASSWORD,
            base_path=ftp_upload_dir,
            home_path="/",
            permissions=(aioftp.Permission("/", readable=True, writable=True),),
        ),
    )

    await Tortoise.init(TORTOISE_ORM)

    server = SurvFTPServer(
        users,
        path_io_factory=aioftp.AsyncPathIO,
        data_ports=range(
            settings.FTP_PASSIVE_PORTS_FROM, settings.FTP_PASSIVE_PORTS_TO
        ),
    )
    await server.run(host=settings.FTP_BIND_HOST, port=settings.FTP_BIND_PORT)


asyncio.run(main())
