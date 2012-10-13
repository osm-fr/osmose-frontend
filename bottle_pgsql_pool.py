'''
Bottle-PgSQL is based on Bottle-MySQL and Bottle-sqlite.
Bottle-PgSQL is a plugin that integrates PostgreSQL with your Bottle
application. It automatically connects to a database at the beginning of a
request, passes the database handle to the route callback and closes the
connection afterwards.

To automatically detect routes that need a database connection, the plugin
searches for route callbacks that require a `db` keyword argument
(configurable) and skips routes that do not. This removes any overhead for
routes that don't need a database connection.

Results are returned as dictionaries.

Usage Example::

    import bottle
    import bottle_pgsql

    app = bottle.Bottle()
    plugin = bottle_pgsql.Plugin('dbname=db user=user password=pass')
    app.install(plugin)

    @app.route('/show/:item')
    def show(item, db):
        db.execute('SELECT * from items where name="%s"', (item,))
        row = db.fetchone()
        if row:
            return template('showitem', page=row)
        return HTTPError(404, "Page not found")
'''

__author__ = "Arif Kurniawan"
__version__ = '0.2-by frodrigo'
__license__ = 'MIT'

### CUT HERE (see setup.py)

import psycopg2
import psycopg2.extras
import psycopg2.pool
import inspect
from bottle import HTTPError, PluginError
from bottle import HTTPResponse


class PgSQLPoolPlugin(object):
    ''' This plugin passes a pgsql database handle to route callbacks
    that accept a `db` keyword argument. If a callback does not expect
    such a parameter, no connection is made. You can override the database
    settings on a per-route basis. '''

    name = 'pgsql'
    api  = 2

    def __init__(self, dsn=None, autocommit=True, dictrows=True,
            keyword='db', minconn=10, maxconn=100):
         self.dsn = dsn
         self.autocommit = autocommit
         self.dictrows = dictrows
         self.keyword = keyword
         self.pool = psycopg2.pool.ThreadedConnectionPool(minconn, maxconn, dsn=dsn, connection_factory=ConnFactory)

    def setup(self, app):
        ''' Make sure that other installed plugins don't affect the same
            keyword argument.'''
        for other in app.plugins:
            if not isinstance(other, PgSQLPoolPlugin): continue
            if other.keyword == self.keyword:
                raise PluginError("Found another pgsql plugin with "\
                "conflicting settings (non-unique keyword).")

    def apply(self, callback, route):
        # Override global configuration with route-specific values.
        conf = route.config.get('pgsql') or {}
        dsn = conf.get('dsn', self.dsn)
        autocommit = conf.get('autocommit', self.autocommit)
        dictrows = conf.get('dictrows', self.dictrows)
        keyword = conf.get('keyword', self.keyword)

        # Test if the original callback accepts a 'db' keyword.
        # Ignore it if it does not need a database handle.
        args = inspect.getargspec(route.callback)[0]
        if keyword not in args:
            return callback

        def wrapper(*args, **kwargs):
            # Connect to the database
            con = self.pool.getconn()
            try:
                # Using DictCursor lets us return result as a dictionary instead of the default list
                if dictrows:
                    cur = con.cursor(cursor_factory=psycopg2.extras.DictCursor)
                else:
                    cur = con.cursor()
            except HTTPResponse, e:
                raise HTTPError(500, "Database Error", e)

            # Add the connection handle as a keyword argument.
            kwargs[keyword] = cur

            try:
                rv = callback(*args, **kwargs)
                if autocommit:
                    con.commit()
            except psycopg2.ProgrammingError, e:
                con.rollback()
                raise HTTPError(500, "Database Error", e)
            except HTTPError, e:
                raise
            except HTTPResponse, e:
                if autocommit:
                    con.commit()
                raise
            finally:
                if con:
                    con.close()
            return rv

        # Replace the route callback with the wrapped one.
        return wrapper


class ConnFactory(psycopg2.extras.DictConnection):
    def __init__(self, dsn):
        psycopg2.extensions.connection.__init__(self, dsn)
        psycopg2.extras.register_hstore(self, unicode=True)


Plugin = PgSQLPoolPlugin
