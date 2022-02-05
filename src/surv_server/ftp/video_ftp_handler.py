from pyftpdlib.handlers import FTPHandler

from surv_server.ftp.ftp_listeners import NewPhotoListener

PHOTO_EXTENSIONS = {'jpg'}


class SurvFTPHandler(FTPHandler):

    photo_extensions = PHOTO_EXTENSIONS

    on_new_photo_listeners: list[NewPhotoListener] = []

    def on_file_received(self, file):
        if self.on_new_photo_listeners:
            for listener in self.on_new_photo_listeners:
                listener.on_new_photo(file)
