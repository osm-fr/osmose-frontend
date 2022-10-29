import asyncio
from bottle import route, abort

from api.false_positive_utils import _get


@route('/false-positive/<uuid:uuid>.json')
def fp_(db, lang, uuid):
    marker, columns = asyncio.run(_get(db, 'false', uuid=uuid))
    if not marker:
        abort(410, "Id is not present in database.")

    marker = dict(marker)
    marker['timestamp'] = str(marker['timestamp'])
    return dict(
        uuid=uuid,
        marker=marker,
    )
