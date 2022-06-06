import asyncio
import logging
import os

import aioftp

from surv_server.ftp.ftp_server import SurvFTPServer
from surv_server.ftp.ftp_user_manager import SurvServerUserManager
from surv_server.settings import settings
from surv_server.tortoise.db import init_db

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.DEBUG
)
logging.root.setLevel(logging.DEBUG)


async def main():
    ftp_upload_dir = os.path.join(settings.DATA_DIR, "ftp")
    os.makedirs(ftp_upload_dir, exist_ok=True)

    users = SurvServerUserManager()

    await init_db()

    server = SurvFTPServer(
        users,
        path_io_factory=aioftp.AsyncPathIO,
        data_ports=range(
            settings.FTP_PASSIVE_PORTS_FROM, settings.FTP_PASSIVE_PORTS_TO
        ),
    )
    await server.run(host=settings.FTP_BIND_HOST, port=settings.FTP_BIND_PORT)


asyncio.run(main())
