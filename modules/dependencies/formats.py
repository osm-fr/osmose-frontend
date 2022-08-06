from fastapi import HTTPException
from starlette import status


def formats(*formats):
    async def f(format: str) -> str:
        if format not in formats:
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail=f"Unsupported media type '{format}'",
            )
        else:
            return format

    return f
