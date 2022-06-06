from pathlib import Path

from tortoise import fields
from tortoise.models import Model

from surv_server.settings import settings


class TelegramChat(Model):
    id = fields.IntField(pk=True)
    telegram_name = fields.CharField(max_length=255, null=False, unique=True)
    enabled = fields.BooleanField(null=False, default=False)
    send_each_photo = fields.BooleanField(default=False, null=False)

    def __str__(self):
        return self.telegram_name


class PhotoRecord(Model):
    id = fields.IntField(pk=True, generated=True)
    token = fields.CharField(max_length=1024, unique=True, null=True)
    ftp_user = fields.ForeignKeyField(
        model_name="surv_server.FtpUser", related_name="photo_records", null=True
    )
    datetime = fields.DatetimeField(auto_now_add=True, null=False)
    fn = fields.CharField(max_length=1024, null=False, unique=False)

    def get_real_path(self) -> Path:
        return self.ftp_user.get_base_path() / self.fn.strip("/")

    def __str__(self):
        return self.fn


class Tenant(Model):
    id = fields.IntField(pk=True, generated=True)
    code = fields.CharField(max_length=128, unique=True, null=False)
    title = fields.CharField(max_length=1024, unique=False, null=True)


class FtpUser(Model):
    id = fields.IntField(pk=True, generated=True)
    tenant = fields.ForeignKeyField(
        model_name="surv_server.Tenant", related_name="ftp_users", null=False
    )
    code = fields.CharField(max_length=256, null=False, unique=False)
    login_hash = fields.CharField(max_length=256, null=False, unique=True)
    password_hash = fields.CharField(max_length=256, null=False, unique=False)

    def __str__(self) -> str:
        return self.code

    def get_base_path(self) -> Path:
        return Path(settings.DATA_DIR) / str(self.tenant_id) / str(self.id)

    class Meta:
        unique_together = (("tenant", "code"),)
