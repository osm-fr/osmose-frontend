from typing import Any, Dict, List, Literal

try:
    # for python < 3.12
    from typing_extensions import TypedDict
except ImportError:
    from typing import TypedDict


class GeoJSONFeature(TypedDict):
    type: Literal["Feature"]
    properties: Dict["str", Any]
    geometry: Dict["str", Any]


class GeoJSONFeatureCollection(TypedDict):
    type: Literal["FeatureCollection"]
    features: List[GeoJSONFeature]
