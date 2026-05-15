\connect main;

-- ---------------------------------------

DROP TABLE IF EXISTS client."Clients" CASCADE;
CREATE TABLE client."Clients"
(
    clientID        SERIAL      PRIMARY KEY,
    firstName       VARCHAR     NOT NULL,
    lastName        VARCHAR     NOT NULL,
    phone           VARCHAR     NOT NULL,
    email           VARCHAR     NULL,
    created_at      TIMESTAMP   NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    updated_at      TIMESTAMP   NULL,
    deleted_at      TIMESTAMP   NULL
);
--
CREATE INDEX ON client."Clients" (clientID);
--
COMMENT ON TABLE client."Clients" is 'Таблица клиентов';
COMMENT ON COLUMN client."Clients".clientID is 'ID клиента в системе';
COMMENT ON COLUMN client."Clients".firstName is 'Имя клиента';
COMMENT ON COLUMN client."Clients".lastName is 'Фамилия клиента';
COMMENT ON COLUMN client."Clients".phone is 'Телефон клиента';
COMMENT ON COLUMN client."Clients".email is 'Почта клиента';
COMMENT ON COLUMN client."Clients".created_at is 'Дата создания записи о клиенте';
COMMENT ON COLUMN client."Clients".updated_at is 'Дата последнего обновления клиента';
COMMENT ON COLUMN client."Clients".deleted_at is 'Дата удаление клиента из системы';

-- ---------------------------------------

GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA client TO main;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA client TO main;