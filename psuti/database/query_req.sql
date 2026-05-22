-- =====================================================================
-- ЗАПРОСЫ К БД «РИЭЛТОРСКАЯ КОМПАНИЯ» — Вариант 12
-- Соответствие требованиям методички (раздел 5, пп. 1-10)
-- СУБД: PostgreSQL | Инструмент: DBeaver
-- =====================================================================

-- =====================================================================
-- 1. INNER JOIN по одному полю
--    Список квартир с названием района
-- =====================================================================
SELECT
    a.address                       AS "Адрес",
    n.name                          AS "Район",
    a.roomCount                     AS "Комнат",
    a.priceTotal                    AS "Цена (руб.)",
    a.floorCurrent                  AS "Этаж"
FROM apartments."Apartments" a
INNER JOIN glossary."Neighborhood" n ON a.neighborhoodID = n.id
WHERE a.isAvailble = true
ORDER BY a.priceTotal;

-- =====================================================================
-- 2. Косвенно связанные таблицы (через промежуточную)
--    Покупатели, которые совершили сделку, с адресом купленной квартиры
-- =====================================================================
SELECT
    c.firstName || ' ' || c.lastName    AS "Покупатель",
    c.phone                             AS "Телефон",
    a.address                           AS "Купленная квартира",
    t.final_price                       AS "Финальная цена",
    t.paid_at                           AS "Дата оплаты"
FROM work."Transactions" t
INNER JOIN client."Clients" c    ON t.buyerClientID  = c.clientID
INNER JOIN apartments."Apartments" a ON t.apartmentID = a.id
WHERE t.paid_at IS NOT NULL
ORDER BY t.paid_at DESC;

-- =====================================================================
-- 3. Связь по нескольким полям / составное условие
--    Сделки, где продавец и покупатель из одного района (по номеру телефона)
--    + тип сделки совпадает с типом в заявке
-- =====================================================================
SELECT
    t.id                                        AS "ID сделки",
    tt.name                                     AS "Тип сделки",
    seller.firstName || ' ' || seller.lastName  AS "Продавец",
    buyer.firstName  || ' ' || buyer.lastName   AS "Покупатель",
    a.address                                   AS "Объект",
    t.final_price                               AS "Цена"
FROM work."Transactions" t
INNER JOIN glossary."TransactionType" tt ON t.transactionTypeID  = tt.id
INNER JOIN client."Clients" seller       ON t.sellerClientID      = seller.clientID
INNER JOIN client."Clients" buyer        ON t.buyerClientID       = buyer.clientID
INNER JOIN apartments."Apartments" a     ON t.apartmentID         = a.id
INNER JOIN work."Requests" r
    ON  r.clientID          = buyer.clientID
    AND r.transactionTypeID = t.transactionTypeID
WHERE t.canceled_at IS NULL
  AND t.terminated_at IS NULL
ORDER BY t.created_at DESC;

-- =====================================================================
-- 4. LEFT OUTER JOIN
--    Все клиенты и их активные заявки (включая тех, у кого нет заявок)
-- =====================================================================
SELECT
    c.clientID                          AS "ID клиента",
    c.firstName || ' ' || c.lastName   AS "ФИО",
    c.phone                             AS "Телефон",
    tt.name                             AS "Тип сделки",
    r.price_from                        AS "Цена от",
    r.price_to                          AS "Цена до",
    r.created_at                        AS "Дата заявки"
FROM client."Clients" c
LEFT JOIN work."Requests" r     ON c.clientID = r.clientID AND r.deleted_at IS NULL
LEFT JOIN glossary."TransactionType" tt ON r.transactionTypeID = tt.id
ORDER BY c.clientID, r.created_at;

-- =====================================================================
-- 5. Рекурсивное соединение (self-join)
--    Клиенты, которые одновременно являются и продавцом и покупателем
--    в разных сделках (агентство работает с ними в двух ролях)
-- =====================================================================
SELECT DISTINCT
    c.clientID                          AS "ID клиента",
    c.firstName || ' ' || c.lastName   AS "ФИО",
    c.phone                             AS "Телефон",
    'Продавец + Покупатель'             AS "Роли"
FROM client."Clients" c
WHERE c.clientID IN (SELECT sellerClientID FROM work."Transactions")
  AND c.clientID IN (SELECT buyerClientID  FROM work."Transactions");

-- =====================================================================
-- 6. Соединение по отношению (неравенство)
--    Квартиры, стоимость которых НИЖЕ среднего по своему типу дома
-- =====================================================================
SELECT
    a.address                   AS "Адрес",
    bt.name                     AS "Тип дома",
    a.priceTotal                AS "Цена объекта",
    avg_t.avg_price::int        AS "Средняя по типу",
    a.priceTotal - avg_t.avg_price::int AS "Разница"
FROM apartments."Apartments" a
INNER JOIN glossary."BuildingType" bt ON a.buildingTypeID = bt.id
INNER JOIN (
    SELECT buildingTypeID, AVG(priceTotal) AS avg_price
    FROM apartments."Apartments"
    GROUP BY buildingTypeID
) avg_t ON a.buildingTypeID = avg_t.buildingTypeID
WHERE a.priceTotal < avg_t.avg_price
ORDER BY bt.name, a.priceTotal;

-- =====================================================================
-- 7. Агрегирующие функции
--    Статистика по районам: кол-во объявлений, мин/макс/средняя цена
-- =====================================================================
SELECT
    n.name                              AS "Район",
    COUNT(a.id)                         AS "Кол-во объявлений",
    MIN(a.priceTotal)                   AS "Мин. цена",
    MAX(a.priceTotal)                   AS "Макс. цена",
    ROUND(AVG(a.priceTotal))            AS "Средняя цена",
    SUM(a.priceTotal)                   AS "Суммарная стоимость",
    COUNT(CASE WHEN a.isAvailble THEN 1 END) AS "Актуальных"
FROM glossary."Neighborhood" n
LEFT JOIN apartments."Apartments" a ON n.id = a.neighborhoodID
GROUP BY n.id, n.name
ORDER BY "Средняя цена" DESC NULLS LAST;

-- =====================================================================
-- 8. Перекрёстный запрос (CROSSTAB / CASE pivot)
--    Количество сделок по типу (строки) и статусу (столбцы)
-- =====================================================================
SELECT
    tt.name                                                             AS "Тип сделки",
    COUNT(CASE WHEN t.paid_at IS NOT NULL
               AND t.canceled_at IS NULL
               AND t.terminated_at IS NULL THEN 1 END)                 AS "Завершена",
    COUNT(CASE WHEN t.canceled_at IS NOT NULL THEN 1 END)              AS "Отменена",
    COUNT(CASE WHEN t.terminated_at IS NOT NULL THEN 1 END)            AS "Расторгнута",
    COUNT(CASE WHEN t.paid_at IS NULL
               AND t.canceled_at IS NULL
               AND t.terminated_at IS NULL THEN 1 END)                 AS "В процессе",
    COUNT(t.id)                                                        AS "Итого"
FROM glossary."TransactionType" tt
LEFT JOIN work."Transactions" t ON tt.id = t.transactionTypeID
GROUP BY tt.id, tt.name
ORDER BY tt.id;

-- =====================================================================
-- 9. Запрос на изменение (UPDATE)
--    9a. Пометить квартиры как недоступные, если по ним есть оплаченная сделка
-- =====================================================================
UPDATE apartments."Apartments"
SET
    isAvailble = false,
    updated_at = CURRENT_TIMESTAMP
WHERE id IN (
    SELECT apartmentID
    FROM work."Transactions"
    WHERE paid_at IS NOT NULL
      AND canceled_at IS NULL
      AND terminated_at IS NULL
)
AND isAvailble = true;

-- 9b. Обновить флаг isLegalOk для объектов без обременений и без судимостей
UPDATE apartments."Apartments"
SET
    isLegalOk  = true,
    updated_at = CURRENT_TIMESTAMP
WHERE encumbrance IS NULL
  AND (courtHistory = '[]'::jsonb OR courtHistory IS NULL)
  AND isLegalOk = false;

-- =====================================================================
-- 10. Запрос с вычисляемым полем
--     Полный прайс-лист: цена за м², комиссия агентства (3%), итого с комиссией
-- =====================================================================
SELECT
    a.address                                           AS "Адрес",
    n.name                                              AS "Район",
    bt.name                                             AS "Тип дома",
    a.roomCount                                         AS "Комнат",
    (a.space->>'total')::numeric                        AS "Площадь, м²",
    a.priceTotal                                        AS "Цена (руб.)",
    ROUND(a.priceTotal::numeric /
          NULLIF((a.space->>'total')::numeric, 0))      AS "Цена за м² (руб.)",
    ROUND(a.priceTotal * 0.03)                          AS "Комиссия агентства 3% (руб.)",
    ROUND(a.priceTotal * 1.03)                          AS "Итого с комиссией (руб.)",
    CASE
        WHEN a.isMortgageAllowed THEN 'Да' ELSE 'Нет'
    END                                                 AS "Ипотека",
    CASE
        WHEN a.isLegalOk THEN 'Проверено' ELSE 'Не проверено'
    END                                                 AS "Юр. чистота"
FROM apartments."Apartments" a
INNER JOIN glossary."Neighborhood" n  ON a.neighborhoodID  = n.id
INNER JOIN glossary."BuildingType" bt ON a.buildingTypeID  = bt.id
WHERE a.isAvailble = true
ORDER BY a.priceTotal;

-- =====================================================================
-- БОНУС: Подзапрос — клиенты с наибольшим числом заявок
-- =====================================================================
SELECT
    c.firstName || ' ' || c.lastName   AS "Клиент",
    c.phone,
    req_count.cnt                       AS "Кол-во заявок"
FROM client."Clients" c
INNER JOIN (
    SELECT clientID, COUNT(*) AS cnt
    FROM work."Requests"
    WHERE deleted_at IS NULL
    GROUP BY clientID
) req_count ON c.clientID = req_count.clientID
ORDER BY req_count.cnt DESC
LIMIT 5;