from typing import Any, Dict, List, Literal, TypedDict


class GeoJSONFeature(TypedDict):
    type: Literal["Feature"]
    properties: Dict["str", Any]
    geometry: Dict["str", Any]


class GeoJSONFeatureCollection(TypedDict):
    type: Literal["FeatureCollection"]
    features: List[GeoJSONFeature]
