def ext_filter(config):
    regexp = r"html|json|geojson|xml|rss|png|svg|pdf|gpx|kml|josm|csv|mvt"

    def to_python(match):
        return (
            match
            if match
            in (
                "html",
                "json",
                "geojson",
                "xml",
                "rss",
                "png",
                "svg",
                "pdf",
                "gpx",
                "kml",
                "josm",
                "csv",
                "mvt",
            )
            else "html"
        )

    def to_url(ext):
        return ext

    return regexp, to_python, to_url


def uuid_filter(config):
    regexp = r"[0-9a-fA-F]{8}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{12}"

    def to_python(match):
        return match

    def to_url(ext):
        return ext

    return regexp, to_python, to_url


def inspect_routes(app):
    for route in app.routes:
        if "mountpoint" in route.config:
            prefix = route.config["mountpoint.prefix"]
            subapp = route.config["mountpoint.target"]

            p = prefix.split("/", 2)[1]
            if not (len(p) == 2 or (len(p) == 5 and p[2] == "_")) or p == "en":
                for prefixes, route in inspect_routes(subapp):
                    yield [prefix] + prefixes, route
        else:
            yield [], route
