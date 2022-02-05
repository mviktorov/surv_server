import logging

from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.servers import FTPServer

from surv_server.ftp.video_ftp_handler import SurvFTPHandler
from surv_server.telegram_bot.surv_server_telegram_bot import VideoServerTelegramBot
from surv_server.settings import settings
import os

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

authorizer = DummyAuthorizer()

ftp_upload_dir = os.path.join(settings.DATA_DIR, "ftp")
os.makedirs(ftp_upload_dir, exist_ok=True)

authorizer.add_user(
    settings.FTP_UPLOAD_USER,
    settings.FTP_UPLOAD_PASSWORD,
    ftp_upload_dir,
    perm=settings.FTP_UPLOAD_PERMISSIONS,
)

telegram_bot = VideoServerTelegramBot(
    bot_token=settings.TELEGRAM_BOT_TOKEN,
    bot_admin=settings.TELEGRAM_BOT_ADMIN,
    chat_ids_fn=os.path.join(settings.DATA_DIR, "chat_ids"),
    allowed_users_fn=os.path.join(settings.DATA_DIR, "allowed_users"),
)

handler = SurvFTPHandler
handler.authorizer = authorizer
handler.on_new_photo_listeners = {telegram_bot}

server = FTPServer((settings.FTP_BIND_HOST, settings.FTP_BIND_PORT), handler)
server.serve_forever()
