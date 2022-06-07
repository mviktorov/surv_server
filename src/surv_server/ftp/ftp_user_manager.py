import bcrypt
from aioftp import AbstractUserManager, User
from tortoise.exceptions import DoesNotExist

from surv_server.crypto.crypto import hash_password
from surv_server.tortoise.models import FtpUser


class SurvFtpUser(User):
    def __init__(self, u: FtpUser):
        super().__init__(
            str(u.id),
            u.password_hash,
            base_path=u.get_base_path(),
        )
        self.user_model = u


class SurvServerUserManager(AbstractUserManager):
    async def find_user(self, login):
        try:
            return await FtpUser.get(login_hash=hash_password(login))
        except (DoesNotExist, ValueError):
            return None

    async def get_user(
        self, login
    ) -> tuple[AbstractUserManager.GetUserResponse, User | None, str]:
        user_model: FtpUser = await self.find_user(login)
        if not user_model:
            return AbstractUserManager.GetUserResponse.ERROR, None, "Unknown user"
        elif not user_model.password_hash:

            return (
                AbstractUserManager.GetUserResponse.OK,
                SurvFtpUser(user_model),
                "Hello Anonymous",
            )
        else:
            return (
                AbstractUserManager.GetUserResponse.PASSWORD_REQUIRED,
                SurvFtpUser(user_model),
                "Password required",
            )

    async def authenticate(self, user: User, password: str):
        return bcrypt.checkpw(password.encode("utf-8"), user.password.encode("utf-8"))
