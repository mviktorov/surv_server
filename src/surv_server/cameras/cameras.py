import re

from surv_server.settings import settings

FN_REGEXP_COMPILED: re.Pattern | None = None


def init():
    global FN_REGEXP_COMPILED
    FN_REGEXP_COMPILED = re.compile(
        settings.FN_REGEXP_TO_CAMERA, re.MULTILINE | re.IGNORECASE
    )


async def extract_camera_name(photo_fn: str) -> str:
    if FN_REGEXP_COMPILED is None:
        init()

    return FN_REGEXP_COMPILED.search(photo_fn).group(1)
