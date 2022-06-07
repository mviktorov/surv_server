import asyncio
import os
from uuid import uuid4

import aioftp

from surv_server.tortoise.models import PhotoRecord


class SurvFTPServer(aioftp.Server):
    async def noop(self, connection, rest):
        connection.response("200", "boring")
        return True

    @aioftp.ConnectionConditions(aioftp.ConnectionConditions.login_required)
    async def mkd(self, connection, rest):
        connection.response("257", "")
        return True

    @aioftp.ConnectionConditions(aioftp.ConnectionConditions.login_required)
    async def cwd(self, connection, rest):
        real_path, virtual_path = self.get_paths(connection, rest)
        connection.current_directory = virtual_path
        connection.response("250", "")
        return True

    @aioftp.ConnectionConditions(aioftp.ConnectionConditions.login_required)
    async def rmd(self, connection, rest):
        connection.response("250", "")
        return True

    @aioftp.ConnectionConditions(aioftp.ConnectionConditions.login_required)
    async def dele(self, connection, rest):
        connection.response("250", "")
        return True

    async def not_implemented(self, connection, rest):
        connection.response("502", "Not implemented")
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

            return True

        real_path, virtual_path = self.get_paths(connection, rest)

        ext = os.path.splitext(virtual_path.name)[1].lower()
        token = str(uuid4())
        fn = token + ext

        photo_record = await PhotoRecord.create(
            fn=fn, ftp_user=connection.user.user_model, token=token
        )
        real_path = photo_record.get_real_path()
        real_path.parent.mkdir(parents=True, exist_ok=True)

        coro = stor_worker(self, connection, rest)
        task = asyncio.create_task(coro)
        connection.extra_workers.add(task)
        code, info = "150", "data transfer started"
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
        self.commands_mapping = {
            "noop": self.noop,
            "abor": self.abor,
            "appe": self.not_implemented,
            "cdup": self.cdup,
            "cwd": self.cwd,
            "dele": self.dele,
            "epsv": self.epsv,
            "list": self.not_implemented,
            "mkd": self.mkd,
            "mlsd": self.not_implemented,
            "mlst": self.not_implemented,
            "pass": self.pass_,
            "pasv": self.pasv,
            "pbsz": self.pbsz,
            "prot": self.prot,
            "pwd": self.pwd,
            "quit": self.quit,
            "rest": self.rest,
            "retr": self.not_implemented,
            "rmd": self.rmd,
            "rnfr": self.not_implemented,
            "rnto": self.not_implemented,
            "stor": self.stor,
            "syst": self.syst,
            "type": self.type,
            "user": self.user,
        }
