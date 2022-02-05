import os.path

from pyftpdlib.handlers import FTPHandler

from surv_server.ftp.ftp_listeners import NewPhotoListener

PHOTO_EXTENSIONS = {"jpg"}


class SurvFTPHandler(FTPHandler):

    photo_extensions = PHOTO_EXTENSIONS

    on_new_photo_listeners: list[NewPhotoListener] = []

    def on_file_received(self, file):
        if self.on_new_photo_listeners:
            ext = os.path.splitext(file)[1]
            if ext and ext[1:].lower() in self.photo_extensions:
                for listener in self.on_new_photo_listeners:
                    listener.on_new_photo(file)
