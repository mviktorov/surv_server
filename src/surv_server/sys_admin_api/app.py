from datetime import date, datetime, time

from fastapi import FastAPI, Form
from fastapi.responses import JSONResponse, RedirectResponse
from pydantic import BaseModel
from tortoise.contrib.pydantic import pydantic_model_creator
from tortoise.exceptions import IntegrityError, DoesNotExist

from surv_server.crypto.crypto import gen_uid, hash_password
from surv_server.tortoise.db import init_db
from surv_server.tortoise.models import Tenant, FtpUser, PhotoRecord

app = FastAPI(title="SurvServer SysAdmin API", version="1.0.0")


tenant_dto = pydantic_model_creator(Tenant)


class FtpUserUpdateDTO(BaseModel):
    code: str


class FtpUserCreateDTO(BaseModel):
    id: int
    code: str
    login: str
    password: str


class FtpUserDTO(BaseModel):
    id: int
    code: str


class PhotoRecordDTO(BaseModel):
    ftp_user: str
    token: str
    datetime: datetime

    @classmethod
    def from_model(cls, p: PhotoRecord):
        return PhotoRecordDTO(
            ftp_user=p.ftp_user.code, token=p.token, datetime=p.datetime
        )


@app.get("/")
async def read_root():
    return RedirectResponse("/docs")


@app.get("/tenants/", response_model=list[tenant_dto])
async def list_tenants():
    return await tenant_dto.from_queryset(Tenant.all())


@app.post("/tenants/", status_code=201, response_model=tenant_dto)
async def create_tenant(code=Form(...), title=Form(...)):
    try:
        t = await Tenant.create(code=code, title=title)
        return await tenant_dto.from_tortoise_orm(t)
    except IntegrityError as ie:
        return JSONResponse({"detail": str(ie)}, status_code=400)


@app.get("/tenants/{tenant_id}/ftp_users/", response_model=list[FtpUserDTO])
async def list_tenant_ftp_users(tenant_id: int):
    return [
        FtpUserDTO(id=u.id, code=u.code)
        for u in await FtpUser.filter(tenant_id=tenant_id)
    ]


@app.post(
    "/tenants/{tenant_id}/ftp_users/",
    status_code=201,
    response_model=FtpUserCreateDTO,
)
async def create_ftp_user(tenant_id: int, code=Form(...)):
    try:
        login = gen_uid(16)
        password = gen_uid(16)
        u = await FtpUser.create(
            tenant_id=tenant_id,
            code=code,
            login_hash=hash_password(login),
            password_hash=hash_password(password),
        )
        return FtpUserCreateDTO(id=u.id, code=u.code, login=login, password=password)
    except IntegrityError as ie:
        return JSONResponse({"detail": str(ie)}, status_code=400)


@app.put(
    "/tenants/{tenant_id}/ftp_users/{ftp_user_id}",
    status_code=200,
    response_model=FtpUserDTO,
)
async def update_ftp_user(tenant_id: int, ftp_user_id: int, data: FtpUserUpdateDTO):
    try:
        u = await FtpUser.get(tenant_id=tenant_id, id=ftp_user_id)
        u.code = data.code
        await u.save()
        return FtpUserDTO(id=u.id, code=u.code)
    except DoesNotExist as dne:
        return JSONResponse({"detail": "tenant_id/ftp_user_id combination not found"})
    except IntegrityError as ie:
        return JSONResponse({"detail": str(ie)}, status_code=400)


@app.put(
    "/tenants/{tenant_id}/ftp_users/{ftp_user_id}/change_auth",
    status_code=200,
    response_model=FtpUserCreateDTO,
)
async def regenerate_login_password_ftp_user(tenant_id: int, ftp_user_id: int):
    try:
        login = gen_uid(16)
        password = gen_uid(16)
        u = await FtpUser.get(tenant_id=tenant_id, id=ftp_user_id)
        u.login_hash = hash_password(login)
        u.password_hash = hash_password(password)
        await u.save()
        return FtpUserCreateDTO(id=u.id, code=u.code, login=login, password=password)
    except DoesNotExist as dne:
        return JSONResponse({"detail": "tenant_id/ftp_user_id combination not found"})
    except IntegrityError as ie:
        return JSONResponse({"detail": str(ie)}, status_code=400)


@app.get("/tenants/{tenant_id}/{ftp_user}/photos/")
async def list_tenant_photos(
    tenant_id: int, ftp_user: str, date_start: date, date_end: date
):
    return [
        PhotoRecordDTO.from_model(model)
        for model in await PhotoRecord.filter(
            ftp_user__tenant_id=tenant_id,
            ftp_user__code=ftp_user,
            datetime__gte=datetime.combine(date_start, time.min),
            datetime__lt=datetime.combine(date_end, time.min),
        ).prefetch_related("ftp_user")
    ]


@app.on_event("startup")
async def startup():
    await init_db()
