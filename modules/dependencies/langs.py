from typing import List, Optional

from fastapi import Request

# Languages API 0.3 middleware


def parse_accept_language(request: Request, langs: List[str]) -> List[str]:
    accept_language = request.headers.get("Accept-Language", "")
    if not langs:
        langs = ["en"]
    langs = list(
        map(lambda lang: lang.split(";")[0].strip(), accept_language.split(","))
    )
    langs += list(map(lambda lang: lang.split("_")[0].lower(), langs))
    return langs


async def langs(request: Request) -> Optional[List[str]]:
    param_lang = request.query_params.get("langs")
    langs: List[str] = param_lang.split(",") if param_lang else ["auto"]
    if langs:
        langs = parse_accept_language(request, langs)
    return langs
