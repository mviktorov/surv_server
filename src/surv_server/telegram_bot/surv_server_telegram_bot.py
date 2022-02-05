import json
import logging

from telegram import Update
from telegram.ext import (
    Updater,
    Dispatcher,
    CommandHandler,
    CallbackContext,
)

from surv_server.ftp.ftp_listeners import NewPhotoListener

logger = logging.getLogger("videoserver.telegram_bot")


class VideoServerTelegramBot(NewPhotoListener):
    def add_chat(self, chat_id: str, username: str):
        self.chat_ids_to_names[chat_id] = username
        self.save_chat_ids()

    def save_chat_ids(self):
        with open(self.chat_ids_fn, "w") as f:
            json.dump(self.chat_ids_to_names, f, indent=2)

    def load_chat_ids(self):
        try:
            with open(self.chat_ids_fn, "r") as f:
                chat_ids = json.load(f)
                self.chat_ids_to_names = dict()
                if chat_ids:
                    self.chat_ids_to_names.update(chat_ids)
        except FileNotFoundError:
            self.chat_ids_to_names = dict()

    def add_allowed_user(self, username: str):
        self.allowed_users.add(username)
        self.save_allowed_users()

    def remove_allowed_user(self, username: str):
        if username not in self.allowed_users:
            return
        self.clean_up_chat_ids()
        self.allowed_users.remove(username)
        self.save_allowed_users()
        self.save_chat_ids()

    def clear_users(self):
        self.allowed_users.clear()
        self.clean_up_chat_ids()
        self.save_allowed_users()
        self.save_chat_ids()

    def clean_up_chat_ids(self):
        self.chat_ids_to_names = {
            chat_id: user_name
            for chat_id, user_name in self.chat_ids_to_names.items()
            if user_name == self.bot_admin or user_name in self.allowed_users
        }

    def save_allowed_users(self):
        with open(self.allowed_users_fn, "w") as f:
            json.dump(list(self.allowed_users), f, indent=2)

    def load_allowed_users(self):
        try:
            with open(self.allowed_users_fn, "r") as f:
                allowed_users = json.load(f)
                self.allowed_users = set()
                if allowed_users:
                    self.allowed_users.update(allowed_users)
        except FileNotFoundError:
            self.allowed_users = set()

    def __init__(
        self,
        bot_token: str,
        bot_admin: str,
        chat_ids_fn: str = "chat_ids",
        allowed_users_fn: str = "allowed_users",
    ) -> None:
        self.allowed_users_fn = allowed_users_fn
        self.allowed_users = set()
        self.chat_ids_fn = chat_ids_fn
        self.bot_admin = bot_admin
        self.updater: Updater = Updater(token=bot_token)
        self.dispatcher: Dispatcher = self.updater.dispatcher
        self.chat_ids_to_names: dict[str, str] = dict()
        self.load_chat_ids()
        self.load_allowed_users()

        def start(update: Update, context: CallbackContext):
            username: str = update.effective_chat.username
            if username != self.bot_admin and username not in self.allowed_users:
                context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text="Hi! This is a private chat bot. Sorry.",
                )
                context.bot.leave_chat(chat_id=update.effective_chat.id)
            else:
                context.bot.send_message(
                    chat_id=update.effective_chat.id, text=f"Hello {username}!"
                )
                self.add_chat(update.effective_chat.id, update.effective_chat.username)

        start_handler = CommandHandler("start", start)
        self.dispatcher.add_handler(start_handler)

        def add_user(update: Update, context: CallbackContext):
            if context.args and context.args[0]:
                self.add_allowed_user(context.args[0])

        def remove_user(update: Update, context: CallbackContext):
            if context.args and context.args[0]:
                self.remove_allowed_user(context.args[0])

        def clear_users(update: Update, context: CallbackContext):
            self.clear_users()

        def list_users(update: Update, context: CallbackContext):
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="\n".join(self.allowed_users)
                if self.allowed_users
                else "Only you.",
            )

        self.dispatcher.add_handler(
            CommandHandler("add_user", add_user, pass_args=True)
        )
        self.dispatcher.add_handler(
            CommandHandler("remove_user", remove_user, pass_args=True)
        )

        self.dispatcher.add_handler(
            CommandHandler("list_users", list_users, pass_args=False)
        )

        self.dispatcher.add_handler(
            CommandHandler("clear_users", clear_users, pass_args=False)
        )

        self.updater.start_polling()

        super().__init__()

    def on_new_photo(self, local_fn: str):
        for chat_id, username in self.chat_ids_to_names.items():
            try:
                with open(local_fn, "rb") as f:
                    self.dispatcher.bot.send_photo(chat_id, f)
            except Exception as ex:
                logger.error(
                    f"Unable to send photo {local_fn} to user {username} (chat_id={chat_id})",
                    exc_info=True,
                )
