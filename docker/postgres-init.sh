#!/bin/bash
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE USER osmose;
    ALTER ROLE osmose WITH PASSWORD '-osmose-';
    CREATE DATABASE osmose_frontend OWNER osmose TEMPLATE template0;
    GRANT ALL PRIVILEGES ON DATABASE osmose_frontend TO osmose;
EOSQL

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "osmose_frontend" <<-EOSQL
    CREATE extension IF NOT EXISTS hstore;
    CREATE extension IF NOT EXISTS pgcrypto;
EOSQL

psql -v ON_ERROR_STOP=1 --username "osmose" --dbname "osmose_frontend" < /schema.sql
psql -v ON_ERROR_STOP=1 --username "osmose" --dbname "osmose_frontend" < /osmose-menu.sql
