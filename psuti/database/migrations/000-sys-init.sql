ALTER SYSTEM SET max_connections = 500;

CREATE DATABASE main with OWNER postgres ENCODING 'UTF8';

\connect main;

CREATE USER main WITH ENCRYPTED PASSWORD 'main_pwd';

CREATE SCHEMA IF NOT EXISTS glossary;
CREATE SCHEMA IF NOT EXISTS client;
CREATE SCHEMA IF NOT EXISTS apartments;
CREATE SCHEMA IF NOT EXISTS work;

ALTER SCHEMA glossary OWNER TO main;
ALTER SCHEMA client OWNER TO main;
ALTER SCHEMA apartments OWNER TO main;
ALTER SCHEMA work OWNER TO main;

ALTER DATABASE main SET search_path TO public, glossary, client, apartments, work;

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

GRANT ALL ON SCHEMA glossary TO main;
GRANT ALL ON SCHEMA client TO main;
GRANT ALL ON SCHEMA apartments TO main;
GRANT ALL ON SCHEMA work TO main;