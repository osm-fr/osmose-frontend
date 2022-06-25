from typing import List, Union

from fastapi import Request

# Languages API 0.3 middleware


def parse_accept_language(request: Request, langs: List[str]) -> List[str]:
    if langs and "auto" in langs:
        langs = request.headers.get("Accept-Language")
    if not langs:
        langs = "en"
    langs = list(map(lambda lang: lang.split(";")[0].strip(), langs.split(",")))
    langs += list(map(lambda lang: lang.split("_")[0].lower(), langs))
    return langs


async def langs(request: Request) -> Union[List[str], None]:
    langs = request.query_params.get("langs") or ["auto"]
    if langs:
        langs = parse_accept_language(request, langs)

    # script_name = requested URL path
    #    if not langs and len(request.script_name) > 3:
    #        langs = [request.script_name[-3:-1]]

    return langs
