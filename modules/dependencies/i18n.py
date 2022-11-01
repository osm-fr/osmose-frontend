import gettext
from typing import Callable, Dict, List

from fastapi import Depends, Request

from modules.dependencies import langs
from modules.utils import LangsNegociation, allowed_languages

domain = "osmose-frontend"
localedir = "web/po/mo"


Translator = Callable[..., str]


def get_languages(request: Request) -> List[str]:
    langs = [None]

    base_path = request.scope.get("root_path")
    print(base_path)
    if base_path and len(base_path) >= 3:
        # Handle longer languages like zh_TW
        if len(base_path) == 6 and base_path[3] == "_":
            tmp_lang = base_path[1:6]
            if tmp_lang in allowed_languages:
                return ([tmp_lang, allowed_languages[0]], False)

        if len(base_path) == 3:
            tmp_lang = base_path[1:3]
            print("tmp_lang", tmp_lang)
            if tmp_lang in allowed_languages:
                return ([tmp_lang, allowed_languages[0]], False)

    if request.headers.get("Accept-Language"):
        langs = request.headers.get("Accept-Language")
        langs = langs.split(",")
        langs = [x.split(";")[0] for x in langs]
        langs = [x.split("-")[0] for x in langs]
        langs = [x for x in langs if x in allowed_languages]

    if len(langs) > 0 and langs[0]:
        langs.append(allowed_languages[0])
        res = []
        for lang in langs:
            if lang not in res:
                res.append(lang)
        return (res, True)
    else:
        return (allowed_languages, True)


cache: Dict[List[str], Translator] = {}


async def i18n(
    request: Request,
    langs: LangsNegociation = Depends(langs.langs),
) -> Translator:
    (languages, redirect) = get_languages(request)
    print(languages)

    k = ",".join(languages)
    if k in cache:
        gt = cache[k]
    else:
        gt = gettext.translation(
            domain, localedir=localedir, languages=languages
        ).gettext
        cache[k] = gt

    return gt
