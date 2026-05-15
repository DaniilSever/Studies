\connect main;

-- ---------------------------------------

DROP TABLE IF EXISTS apartments."Apartments" CASCADE;
CREATE TABLE apartments."Apartments"
(
    id                  uuid        PRIMARY KEY,
    address             VARCHAR     NOT NULL,
    buildingTypeID      INTEGER     NOT NULL REFERENCES glossary."BuildingType" (id),
    buildingYear        INTEGER     NOT NULL,
    neighborhoodID      INTEGER     NOT NULL REFERENCES glossary."Neighborhood" (id),
    floorsTotal         INTEGER     NOT NULL,
    floorCurrent        INTEGER     NOT NULL,
    isThereList         BOOLEAN     NOT NULL DEFAULT True,
    countLift           INTEGER     NOT NULL,
    liftType            INTEGER     NOT NULL,
    roomCount           INTEGER     NOT NULL,
    priceTotal          INTEGER     NOT NULL,
    isMortgageAllowed   BOOLEAN     NOT NULL DEFAULT True,
    isTaxDeduction      BOOLEAN     NOT NULL DEFAULT False,
    space               jsonb       NOT NULL,
    ownershipType       VARCHAR     NOT NULL,
    encumbrance         VARCHAR     NULL,
    courtHistory        jsonb       NULL,
    isLegalOk           BOOLEAN     NOT NULL DEFAULT False,
    isAvailble          BOOLEAN     NOT NULL DEFAULT True,
    sellerID            INTEGER     NOT NULL REFERENCES client."Clients" (clientID),
    created_at          TIMESTAMP   NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    updated_at          TIMESTAMP   NULL,
    deleted_at          TIMESTAMP   NULL
);
--
CREATE INDEX ON apartments."Apartments" (id);
CREATE INDEX ON apartments."Apartments" (address);
CREATE INDEX ON apartments."Apartments" (floorCurrent);
CREATE INDEX ON apartments."Apartments" (roomCount);
CREATE INDEX ON apartments."Apartments" (priceTotal);
CREATE INDEX ON apartments."Apartments" (isAvailble);
--
COMMENT ON TABLE apartments."Apartments" is 'Таблица объявлений о продаже';
COMMENT ON COLUMN apartments."Apartments".id is 'ID объявления';
COMMENT ON COLUMN apartments."Apartments".address is 'Адрес дома';
COMMENT ON COLUMN apartments."Apartments".buildingTypeID is 'ID типа дома';
COMMENT ON COLUMN apartments."Apartments".buildingYear is 'Год постройки дома';
COMMENT ON COLUMN apartments."Apartments".neighborhoodID is 'ID района';
COMMENT ON COLUMN apartments."Apartments".floorsTotal is 'Количество этажей в доме';
COMMENT ON COLUMN apartments."Apartments".floorCurrent is 'Этаж помещения';
COMMENT ON COLUMN apartments."Apartments".isThereList is 'Имеется ли лифт';
COMMENT ON COLUMN apartments."Apartments".countLift is 'Количество лифтов';
COMMENT ON COLUMN apartments."Apartments".liftType is 'Тип лифта/оф';
COMMENT ON COLUMN apartments."Apartments".roomCount is 'Количество комнат';
COMMENT ON COLUMN apartments."Apartments".priceTotal is 'Полная стоимость';
COMMENT ON COLUMN apartments."Apartments".isMortgageAllowed is 'Возможно ли ипотека';
COMMENT ON COLUMN apartments."Apartments".isTaxDeduction is 'Возможен ли налоговый вычет';
COMMENT ON COLUMN apartments."Apartments".space is 'Пространство помещения';
COMMENT ON COLUMN apartments."Apartments".ownershipType is 'Собственность';
COMMENT ON COLUMN apartments."Apartments".encumbrance is 'Обременения';
COMMENT ON COLUMN apartments."Apartments".courtHistory is 'История судимостей';
COMMENT ON COLUMN apartments."Apartments".isLegalOk is 'Проверил ли юрист';
COMMENT ON COLUMN apartments."Apartments".isAvailble is 'Актуально ли';
COMMENT ON COLUMN apartments."Apartments".sellerID is 'ID продовца';
COMMENT ON COLUMN apartments."Apartments".created_at is 'Когда создано объявление';
COMMENT ON COLUMN apartments."Apartments".updated_at is 'Когда обновлено объявление';
COMMENT ON COLUMN apartments."Apartments".deleted_at is 'Когда удалено объявление';

-- ---------------------------------------

GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA apartments TO main;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA apartments TO main;