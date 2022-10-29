import asyncio
from bottle import route, request, redirect
from modules.dependencies.database import get_dbconn
from modules.dependencies.commons_params import params as async_params
from modules_legacy.params import Params
from modules_legacy import utils, query, query_meta
from api.user_utils import _user_count
from collections import defaultdict


@route('/map')
def errors():
    redirect("map/?" + request.query_string)


@route('/map/.json')
def index(db, user, lang):
    if request.query_string:
        redirect("./#" + request.query_string)

    tags = query_meta._tags(db)
    countries = query_meta._countries(db)

    categories = query_meta._items(db, langs = lang)

    item_levels = {'1': set(), '2': set(), '3': set()}
    for categ in categories:
        for item in categ['items']:
            del(item['number'])
            for index, classs in enumerate(item['class']):
                item['class'][index] = {
                    'class': classs['class'],
                    'title': classs['title'],
                }
            for level in item['levels']:
                item_levels[str(level['level'])].add(item['item'])

    item_levels['1,2'] = item_levels['1'] | item_levels['2']
    item_levels['1,2,3'] = item_levels['1,2'] | item_levels['3']
    item_levels = {k: list(v) for k, v in item_levels.items()}

    sql = """
SELECT
    timestamp
FROM
    updates_last
ORDER BY
    timestamp
LIMIT
    1
OFFSET
    (SELECT COUNT(*)/2 FROM updates_last)
;
"""
    db.execute(sql)
    timestamp = db.fetchone()
    timestamp = str(timestamp[0]) if timestamp and timestamp[0] else None

    if user != None:
        if user:
            async def t(user):
                return await _user_count(await async_params(), await get_dbconn(), user)
            user_error_count = asyncio.run(t(user))
        else: # user == False
            user = '[user name]'
            user_error_count = {1: 0, 2: 0, 3: 0}
    else:
        user_error_count = None

    return dict(categories=categories, tags=tags, countries=countries, item_levels=item_levels,
        main_project=utils.main_project, timestamp=timestamp, languages_name=utils.languages_name,
        website=utils.website, remote_url_read=utils.remote_url_read,
        user=user, user_error_count=user_error_count, main_website=utils.main_website)
