import asyncio
import os
from pathlib import PurePosixPath, Path
from uuid import uuid4

import aioftp

from surv_server.ftp.ftp_user_manager import SurvFtpUser
from surv_server.settings import settings
from surv_server.tortoise.models import PhotoRecord


class FTPEventHandler:
    def __init__(self) -> None:
        super().__init__()
        self.photo_extensions = {
            ext.lower()
            for ext in settings.ALLOWED_PHOTO_EXTENSIONS_TO_SEND_CSV.split(",")
        }

    async def file_stored(
        self, user: SurvFtpUser, virtual_path: PurePosixPath, real_path: Path
    ):
        if (
            os.path.splitext(virtual_path.name)[1].strip(".").lower()
            in self.photo_extensions
        ):
            fn = virtual_path.as_posix()
            await PhotoRecord(
                fn=fn, ftp_user_id=user.user_id, token=str(uuid4())
            ).save()


class SurvFTPServer(aioftp.Server):
    async def noop(self, connection, rest):
        connection.response("200", "boring")
        return True

    @aioftp.ConnectionConditions(
        aioftp.ConnectionConditions.login_required,
        aioftp.ConnectionConditions.passive_server_started,
    )
    @aioftp.PathPermissions(aioftp.PathPermissions.writable)
    async def stor(self, connection, rest, mode="wb"):
        @aioftp.ConnectionConditions(
            aioftp.ConnectionConditions.data_connection_made,
            wait=True,
            fail_code="425",
            fail_info="Can't open data connection",
        )
        @aioftp.worker
        async def stor_worker(self: SurvFTPServer, con: aioftp.Connection, rest):
            user = con.user
            stream = con.data_connection
            del con.data_connection
            if con.restart_offset:
                file_mode = "r+b"
            else:
                file_mode = mode
            file_out = con.path_io.open(real_path, mode=file_mode)
            async with file_out, stream:
                if con.restart_offset:
                    await file_out.seek(con.restart_offset)
                async for data in stream.iter_by_block(con.block_size):
                    await file_out.write(data)
            con.response("226", "data transfer done")

            await self.ftp_event_handler.file_stored(user, virtual_path, real_path)
            return True

        real_path, virtual_path = self.get_paths(connection, rest)
        if await connection.path_io.is_dir(real_path.parent):
            coro = stor_worker(self, connection, rest)
            task = asyncio.create_task(coro)
            connection.extra_workers.add(task)
            code, info = "150", "data transfer started"
        else:
            code, info = "550", "path unreachable"
        connection.response(code, info)
        return True

    def __init__(
        self,
        users=None,
        *,
        block_size=aioftp.DEFAULT_BLOCK_SIZE,
        socket_timeout=None,
        idle_timeout=None,
        wait_future_timeout=1,
        path_timeout=None,
        path_io_factory=aioftp.pathio.PathIO,
        maximum_connections=None,
        read_speed_limit=None,
        write_speed_limit=None,
        read_speed_limit_per_connection=None,
        write_speed_limit_per_connection=None,
        data_ports=None,
        encoding="utf-8",
        ssl=None,
    ):
        super().__init__(
            users,
            block_size=block_size,
            socket_timeout=socket_timeout,
            idle_timeout=idle_timeout,
            wait_future_timeout=wait_future_timeout,
            path_timeout=path_timeout,
            path_io_factory=path_io_factory,
            maximum_connections=maximum_connections,
            read_speed_limit=read_speed_limit,
            write_speed_limit=write_speed_limit,
            read_speed_limit_per_connection=read_speed_limit_per_connection,
            write_speed_limit_per_connection=write_speed_limit_per_connection,
            data_ports=data_ports,
            encoding=encoding,
            ssl=ssl,
        )
        self.ftp_event_handler = FTPEventHandler()
        self.commands_mapping["noop"] = self.noop
