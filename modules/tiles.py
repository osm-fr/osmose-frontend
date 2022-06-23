import math
from typing import Tuple


# https://wiki.openstreetmap.org/wiki/Slippy_map_tilenames#Python
def lonlat2tile(lon_deg: float, lat_deg: float, zoom: int) -> Tuple[int, int]:
    lat_rad = math.radians(lat_deg)
    n = 2.0 ** zoom
    xtile = int((lon_deg + 180.0) / 360.0 * n)
    ytile = int(
        (1.0 - math.log(math.tan(lat_rad) + (1 / math.cos(lat_rad))) / math.pi)
        / 2.0
        * n
    )
    return (xtile, ytile)


# https://wiki.openstreetmap.org/wiki/Slippy_map_tilenames#Python
def tile2lonlat(xtile: int, ytile: int, zoom: int) -> Tuple[float, float]:
    n = 2.0 ** zoom
    lon_deg = xtile / n * 360.0 - 180.0
    lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * ytile / n)))
    lat_deg = math.degrees(lat_rad)
    return (lon_deg, lat_deg)


def bbox2tile(
    min_lon: float, min_lat: float, max_lon: float, max_lat: float
) -> Tuple[int, int, int]:
    # Note: Naive implementation
    tile = (0, 0)
    min_tile = max_tile = tile
    z = 0
    while z < 19 and min_tile == max_tile:
        tile = min_tile
        min_tile = lonlat2tile(min_lon, min_lat, z)
        max_tile = lonlat2tile(max_lon, max_lat, z)
        z += 1
    return (tile[0], tile[1], z - 2)
