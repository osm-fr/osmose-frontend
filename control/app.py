import bottle

from modules_legacy import bottle_pgsql, utils


class OsmoseControlBottle(bottle.Bottle):
    def default_error_handler(self, res):
        bottle.response.content_type = "text/plain"
        return res.body


app = OsmoseControlBottle()
bottle.default_app.push(app)

app.install(bottle_pgsql.Plugin(utils.db_string))

bottle.default_app.pop()

if __name__ == "__main__":
    bottle.run(app=app, host="0.0.0.0", port=20009, reloader=True, debug=True)
