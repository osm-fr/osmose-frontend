import asyncio
from bottle import route, abort
from modules.dependencies.database import get_dbconn
from modules_legacy import utils

from api.issue_utils import _get, _expand_tags, t2l


@route('/issue/<uuid:uuid>.json')
def display(db, lang, uuid):
    async def t(uuid):
        return await _get(await get_dbconn(), uuid=uuid)
    marker = asyncio.run(t(uuid))
    if not marker:
        abort(410, "Id is not present in database.")

    for e in marker['elems'] or []:
        e['tags'] = _expand_tags(e.get('tags', {}), t2l.checkTags(e.get('tags', {})))

    for fix_group in marker['fixes'] or []:
        for f in fix_group:
            f['create'] = _expand_tags(f['create'], t2l.checkTags(f['create']))
            f['modify'] = _expand_tags(f['modify'], t2l.checkTags(f['modify']))
            f['delete'] = _expand_tags(f['delete'], {}, True)

    marker = dict(marker)
    marker['timestamp'] = str(marker['timestamp'])
    return dict(
        uuid = uuid,
        marker = marker,
        main_website = utils.main_website,
    )
