\connect main;

-- ---------------------------------------

DROP TABLE IF EXISTS glossary."Neighborhood" CASCADE;
CREATE TABLE glossary."Neighborhood"
(
    id      SERIAL      PRIMARY KEY,
    name    VARCHAR     NOT NULL
);
--
COMMENT ON TABLE glossary."Neighborhood" is 'Районы города';
COMMENT ON COLUMN glossary."Neighborhood".id is 'ID района';
COMMENT ON COLUMN glossary."Neighborhood".name is 'Название района';

-- ---------------------------------------

DROP TABLE IF EXISTS glossary."BuildingType" CASCADE;
CREATE TABLE glossary."BuildingType"
(
    id              SERIAL       PRIMARY KEY,
    name            VARCHAR      NOT NULL,
    specifications  VARCHAR      NOT NULL
);
--
COMMENT ON TABLE glossary."BuildingType" is 'Типы постройки';
COMMENT ON COLUMN glossary."BuildingType".id is 'ID типа';
COMMENT ON COLUMN glossary."BuildingType".name is 'Название типа';
COMMENT ON COLUMN glossary."BuildingType".specifications is 'Особенности';

-- ---------------------------------------

DROP TABLE IF EXISTS glossary."TransactionType" CASCADE;
CREATE TABLE glossary."TransactionType"
(
    id      SERIAL      PRIMARY KEY,
    name    VARCHAR     NOT NULL
);
--
COMMENT ON TABLE glossary."TransactionType" is 'Типы сделки';
COMMENT ON COLUMN glossary."TransactionType".id is 'ID типа';
COMMENT ON COLUMN glossary."TransactionType".name is 'Название типа';

-- ---------------------------------------

GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA glossary TO main;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA glossary TO main