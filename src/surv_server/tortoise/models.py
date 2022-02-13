from tortoise import fields
from tortoise.models import Model


class TelegramChat(Model):
    id = fields.IntField(pk=True)
    telegram_name = fields.CharField(max_length=255, null=False, unique=True)
    enabled = fields.BooleanField(null=False, default=False)
    send_each_photo = fields.BooleanField(default=False, null=False)

    def __str__(self):
        return self.telegram_name


class PhotoRecord(Model):
    id = fields.IntField(pk=True)
    datetime = fields.DatetimeField(auto_now_add=True, null=False)
    fn = fields.CharField(max_length=1024, null=False, unique=True)
    camera_name = fields.CharField(max_length=255, null=False)

    def __str__(self):
        return self.fn
