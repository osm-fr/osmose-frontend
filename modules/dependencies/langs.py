from typing import List, Optional

from fastapi import Request

# Languages API 0.3 middleware


def parse_accept_language(request: Request, langs: List[str]) -> List[str]:
    if langs and "auto" in langs:
        accept_language = request.headers.get("Accept-Language")
    if not langs:
        accept_language = "en"
    langs = list(
        map(lambda lang: lang.split(";")[0].strip(), accept_language.split(","))
    )
    langs += list(map(lambda lang: lang.split("_")[0].lower(), langs))
    return langs


async def langs(request: Request) -> Optional[List[str]]:
    langs = request.query_params.get("langs") or ["auto"]
    if langs:
        langs = parse_accept_language(request, langs)
    return langs
