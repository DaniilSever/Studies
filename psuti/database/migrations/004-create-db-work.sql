\connect main;

-- ---------------------------------------

DROP TABLE IF EXISTS work."Requests" CASCADE;
CREATE TABLE work."Requests"
(
    id                  uuid        PRIMARY KEY,
    clientID            INTEGER     NOT NULL REFERENCES client."Clients" (clientID),
    transactionTypeID   INTEGER     NOT NULL REFERENCES glossary."TransactionType" (id),
    wishes              jsonb       NOT NULL,
    price_from          INTEGER     NULL,
    price_to            INTEGER     NULL,
    created_at          TIMESTAMP   NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    updated_at          TIMESTAMP   NULL,
    deleted_at          TIMESTAMP   NULL
);
--
CREATE INDEX ON work."Requests" (id);
--
COMMENT ON TABLE work."Requests" is 'Таблица объявлений о продаже';
COMMENT ON COLUMN work."Requests".id is 'ID заявки';
COMMENT ON COLUMN work."Requests".clientID is 'ID клиента';
COMMENT ON COLUMN work."Requests".transactionTypeID is 'Тип сделки';
COMMENT ON COLUMN work."Requests".wishes is 'Пожелания клиента';
COMMENT ON COLUMN work."Requests".price_from is 'Стартовая цена';
COMMENT ON COLUMN work."Requests".price_to is 'Конечная цена';
COMMENT ON COLUMN work."Requests".created_at is 'Когда создана заявка';
COMMENT ON COLUMN work."Requests".updated_at is 'Когда обновлена заявка';
COMMENT ON COLUMN work."Requests".deleted_at is 'Когда удалена заявка';

-- ---------------------------------------

DROP TABLE IF EXISTS work."Transactions" CASCADE;
CREATE TABLE work."Transactions"
(
    id                  uuid        PRIMARY KEY,
    sellerClientID      INTEGER     NOT NULL REFERENCES client."Clients" (clientID),
    buyerClientID       INTEGER     NOT NULL REFERENCES client."Clients" (clientID),
    transactionTypeID   INTEGER     NOT NULL REFERENCES glossary."TransactionType" (id),
    apartmentID         uuid        NOT NULL REFERENCES apartments."Apartments" (id),
    final_price         INTEGER     NOT NULL,
    created_at          TIMESTAMP   NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    paid_at             TIMESTAMP   NULL,
    canceled_at         TIMESTAMP   NULL,
    terminated_at       TIMESTAMP   NULL,
    termination_reason  VARCHAR     NULL
);
--
CREATE INDEX ON work."Transactions" (id);
--
COMMENT ON TABLE work."Transactions" is 'Таблица объявлений о продаже';
COMMENT ON COLUMN work."Transactions".id is 'ID транзакции';
COMMENT ON COLUMN work."Transactions".sellerClientID is 'ID продавца';
COMMENT ON COLUMN work."Transactions".buyerClientID is 'ID покупателя';
COMMENT ON COLUMN work."Transactions".transactionTypeID is 'Тип сделки';
COMMENT ON COLUMN work."Transactions".apartmentID is 'ID помещения';
COMMENT ON COLUMN work."Transactions".final_price is 'Финальная цена';
COMMENT ON COLUMN work."Transactions".created_at is 'Когда создана заявка';
COMMENT ON COLUMN work."Transactions".paid_at is 'Когда оплачено';
COMMENT ON COLUMN work."Transactions".canceled_at is 'Когда отменено';
COMMENT ON COLUMN work."Transactions".terminated_at is 'Когда расторжено';
COMMENT ON COLUMN work."Transactions".termination_reason is 'Причина расторжения транзакции';

-- ---------------------------------------

GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA work TO main;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA work TO main;

ALTER ROLE main SET search_path TO glossary, client, apartments, work, public;