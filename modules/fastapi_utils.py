from fastapi.responses import JSONResponse, Response


class XMLResponse(Response):
    media_type = "text/xml; charset=utf-8"


class GeoJSONResponse(JSONResponse):
    media_type = "application/vnd.geo+json"
