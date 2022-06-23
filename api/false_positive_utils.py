from typing import Union
from uuid import UUID


def _get(db, status, err_id: Union[int, None] = None, uuid: Union[UUID, None] = None):
    columns = [
        "markers_status.item",
        "source_id",
        "markers_status.class",
        "lat::float",
        "lon::float",
        "title",
        "subtitle",
        "date AS timestamp",
    ]

    if err_id:
        sql = (
            "SELECT "
            + ",".join(columns)
            + """
        FROM
            markers_status
            JOIN class ON
                class.item = markers_status.item AND
                class.class = markers_status.class
        WHERE
            status = %s AND
            uuid_to_bigint(uuid) = %s
        """
        )
        db.execute(sql, (status, err_id))
    else:
        sql = (
            "SELECT "
            + ",".join(columns)
            + """
        FROM
            markers_status
        JOIN class ON
            class.item = markers_status.item AND
            class.class = markers_status.class
        WHERE
            status = %s AND
            uuid = %s
        """
        )
        db.execute(sql, (status, uuid))

    marker = db.fetchone()

    return (marker, columns)
