\connect main

--- GLOSSARY

INSERT INTO glossary."Neighborhood" (name) VALUES
('Центральный'),
('Северный'),
('Южный'),
('Западный'),
('Восточный'),
('Заречный'),
('Приморский'),
('Новый'),
('Академический'),
('Советский');

INSERT INTO glossary."BuildingType" (name, specifications) VALUES
('Панельный',       'Типовые панельные серии, 5-16 этажей, 1960-1990 гг.'),
('Кирпичный',       'Монолитная кладка, высокая тепло/звукоизоляция'),
('Монолитный',      'Современное монолитное строительство, свободная планировка'),
('Деревянный',      'Брус или бревно, частный сектор'),
('Блочный',         'Крупноблочные серии, аналог панельного'),
('Сталинский',      'Постройки 1930-1950 гг., высокие потолки, толстые стены'),
('Хрущёвка',        'Типовые серии 1957-1975 гг., 4-5 этажей'),
('Брежневка',       'Улучшенные серии 1965-1980 гг.'),
('Монолитно-кирпичный', 'Комбинированная технология, премиум-класс'),
('Каркасный',       'Быстровозводимые каркасные конструкции');

INSERT INTO glossary."TransactionType" (name) VALUES
('Продажа'),
('Аренда долгосрочная'),
('Аренда краткосрочная'),
('Обмен'),
('Ипотека');

-- Clients

INSERT INTO client."Clients" (firstName, lastName, phone, email) VALUES
('Александр',   'Иванов',       '+79161234501', 'ivanov@mail.ru'),
('Мария',       'Петрова',      '+79161234502', 'petrova@gmail.com'),
('Дмитрий',     'Сидоров',      '+79161234503', NULL),
('Елена',       'Козлова',      '+79161234504', 'kozlova@yandex.ru'),
('Сергей',      'Новиков',      '+79161234505', 'novikov@mail.ru'),
('Ольга',       'Морозова',     '+79161234506', NULL),
('Андрей',      'Волков',       '+79161234507', 'volkov@gmail.com'),
('Наталья',     'Алексеева',    '+79161234508', 'alekseeva@mail.ru'),
('Иван',        'Лебедев',      '+79161234509', NULL),
('Татьяна',     'Соколова',     '+79161234510', 'sokolova@yandex.ru'),
('Михаил',      'Попов',        '+79161234511', 'popov@gmail.com'),
('Анна',        'Захарова',     '+79161234512', NULL),
('Павел',       'Семёнов',      '+79161234513', 'semenov@mail.ru'),
('Светлана',    'Егорова',      '+79161234514', 'egorova@gmail.com'),
('Николай',     'Фёдоров',      '+79161234515', NULL),
('Юлия',        'Орлова',       '+79161234516', 'orlova@yandex.ru'),
('Владимир',    'Кузнецов',     '+79161234517', 'kuznetsov@mail.ru'),
('Ирина',       'Тихонова',     '+79161234518', NULL),
('Алексей',     'Громов',       '+79161234519', 'gromov@gmail.com'),
('Екатерина',   'Беляева',      '+79161234520', 'belyaeva@mail.ru'),
('Роман',       'Шилов',        '+79161234521', NULL),
('Вера',        'Панова',       '+79161234522', 'panova@yandex.ru'),
('Артём',       'Комаров',      '+79161234523', 'komarov@gmail.com'),
('Людмила',     'Щербакова',    '+79161234524', NULL),
('Геннадий',    'Яковлев',      '+79161234525', 'yakovlev@mail.ru');

-- APARTMENTS

INSERT INTO apartments."Apartments" (
    id, address, buildingTypeID, buildingYear, neighborhoodID,
    floorsTotal, floorCurrent, isThereList, countLift, liftType,
    roomCount, priceTotal, isMortgageAllowed, isTaxDeduction,
    space, ownershipType, encumbrance, courtHistory,
    isLegalOk, isAvailble, sellerID
) VALUES
(uuid_generate_v4(), 'ул. Ленина, д.5, кв.12',         1, 1985, 1, 9,  3,  true,  1, 1, 2, 4200000,  true,  false, '{"total":52,"living":30,"kitchen":8}',   'Единоличная',  NULL,           '[]',                                         true,  true,  1),
(uuid_generate_v4(), 'пр. Победы, д.18, кв.45',        3, 2010, 2, 17, 7,  true,  2, 1, 3, 7500000,  true,  true,  '{"total":78,"living":50,"kitchen":12}',  'Долевая',      NULL,           '[]',                                         true,  true,  2),
(uuid_generate_v4(), 'ул. Советская, д.32, кв.8',      2, 1975, 3, 5,  2,  false, 0, 0, 1, 2800000,  false, false, '{"total":34,"living":18,"kitchen":6}',   'Единоличная',  'Залог банка',  '[{"year":2019,"case":"Спор о наследстве"}]', false, true,  3),
(uuid_generate_v4(), 'ул. Гагарина, д.11, кв.99',      1, 1992, 4, 12, 11, true,  1, 2, 3, 5600000,  true,  true,  '{"total":65,"living":42,"kitchen":10}',  'Единоличная',  NULL,           '[]',                                         true,  true,  4),
(uuid_generate_v4(), 'пер. Садовый, д.3, кв.2',        4, 1960, 5, 2,  1,  false, 0, 0, 1, 1900000,  false, false, '{"total":28,"living":16,"kitchen":5}',   'Единоличная',  NULL,           '[]',                                         true,  true,  5),
(uuid_generate_v4(), 'ул. Мира, д.77, кв.201',         3, 2018, 1, 25, 18, true,  3, 1, 4, 12000000, true,  true,  '{"total":105,"living":72,"kitchen":18}', 'Долевая',      NULL,           '[]',                                         true,  true,  6),
(uuid_generate_v4(), 'ул. Строителей, д.14, кв.56',    5, 1980, 6, 9,  5,  true,  1, 1, 2, 3900000,  true,  false, '{"total":48,"living":28,"kitchen":7}',   'Единоличная',  NULL,           '[]',                                         true,  true,  7),
(uuid_generate_v4(), 'пр. Молодёжный, д.22, кв.15',    9, 2015, 2, 20, 14, true,  2, 1, 3, 8900000,  true,  true,  '{"total":88,"living":58,"kitchen":14}',  'Единоличная',  NULL,           '[]',                                         true,  true,  8),
(uuid_generate_v4(), 'ул. Чехова, д.6, кв.33',         6, 1955, 3, 4,  3,  false, 0, 0, 3, 3100000,  false, false, '{"total":60,"living":40,"kitchen":8}',   'Долевая',      'Рента',        '[{"year":2021,"case":"Иск о выселении"}]',   false, true,  9),
(uuid_generate_v4(), 'ул. Пушкина, д.41, кв.7',        2, 1968, 7, 5,  4,  false, 0, 0, 2, 2500000,  false, false, '{"total":42,"living":26,"kitchen":6}',   'Единоличная',  NULL,           '[]',                                         true,  true,  10),
(uuid_generate_v4(), 'бул. Цветочный, д.9, кв.88',     3, 2020, 8, 16, 12, true,  2, 1, 2, 6700000,  true,  true,  '{"total":72,"living":48,"kitchen":11}',  'Единоличная',  NULL,           '[]',                                         true,  true,  11),
(uuid_generate_v4(), 'ул. Лесная, д.2, кв.19',         1, 1988, 9, 10, 9,  true,  1, 2, 2, 4800000,  true,  false, '{"total":55,"living":34,"kitchen":9}',   'Единоличная',  NULL,           '[]',                                         true,  true,  12),
(uuid_generate_v4(), 'ул. Комсомольская, д.55, кв.3',  7, 1978, 10, 9, 8,  true,  1, 1, 1, 3300000,  true,  false, '{"total":44,"living":27,"kitchen":7}',   'Единоличная',  NULL,           '[]',                                         true,  true,  1),
(uuid_generate_v4(), 'пр. Северный, д.100, кв.412',    3, 2022, 2, 22, 16, true,  3, 1, 5, 15000000, true,  true,  '{"total":130,"living":90,"kitchen":20}', 'Долевая',      NULL,           '[]',                                         true,  true,  2),
(uuid_generate_v4(), 'ул. Речная, д.7, кв.44',         2, 1972, 6, 5,  3,  false, 0, 0, 1, 2200000,  false, false, '{"total":36,"living":20,"kitchen":6}',   'Единоличная',  NULL,           '[]',                                         true,  false, 3);

-- Work

INSERT INTO work."Requests" (
    id, clientID, transactionTypeID, wishes, price_from, price_to
) VALUES
(uuid_generate_v4(), 13, 1, '{"rooms":2,"floor_min":2,"floor_max":10,"district":"Центральный"}',    3000000,  6000000),
(uuid_generate_v4(), 14, 1, '{"rooms":3,"floor_min":1,"floor_max":20,"district":"Северный"}',       5000000,  9000000),
(uuid_generate_v4(), 15, 2, '{"rooms":1,"floor_min":1,"floor_max":5,"district":"Любой"}',           15000,    30000),
(uuid_generate_v4(), 16, 1, '{"rooms":4,"floor_min":3,"floor_max":15,"district":"Западный"}',       8000000,  14000000),
(uuid_generate_v4(), 17, 2, '{"rooms":2,"floor_min":2,"floor_max":8,"district":"Центральный"}',     25000,    50000),
(uuid_generate_v4(), 18, 1, '{"rooms":1,"floor_min":1,"floor_max":9,"district":"Южный"}',           1800000,  3500000),
(uuid_generate_v4(), 19, 1, '{"rooms":2,"floor_min":4,"floor_max":12,"district":"Восточный"}',      4000000,  7000000),
(uuid_generate_v4(), 20, 3, '{"rooms":1,"floor_min":1,"floor_max":3,"district":"Центральный"}',     2000,     5000),
(uuid_generate_v4(), 21, 1, '{"rooms":3,"floor_min":2,"floor_max":16,"district":"Академический"}',  6000000,  10000000),
(uuid_generate_v4(), 22, 1, '{"rooms":2,"floor_min":1,"floor_max":6,"district":"Заречный"}',        3500000,  5500000),
(uuid_generate_v4(), 23, 2, '{"rooms":3,"floor_min":3,"floor_max":10,"district":"Северный"}',       40000,    70000),
(uuid_generate_v4(), 24, 1, '{"rooms":1,"floor_min":2,"floor_max":9,"district":"Советский"}',       2000000,  4000000),
(uuid_generate_v4(), 25, 1, '{"rooms":2,"floor_min":5,"floor_max":20,"district":"Западный"}',       5500000,  8500000),
(uuid_generate_v4(), 13, 1, '{"rooms":3,"floor_min":1,"floor_max":12,"district":"Приморский"}',     4500000,  7500000),
(uuid_generate_v4(), 14, 2, '{"rooms":2,"floor_min":2,"floor_max":7,"district":"Любой"}',           20000,    40000),
(uuid_generate_v4(), 15, 1, '{"rooms":1,"floor_min":3,"floor_max":10,"district":"Центральный"}',    2500000,  4500000),
(uuid_generate_v4(), 16, 1, '{"rooms":2,"floor_min":1,"floor_max":5,"district":"Южный"}',           3000000,  5000000),
(uuid_generate_v4(), 17, 1, '{"rooms":4,"floor_min":5,"floor_max":25,"district":"Новый"}',          9000000,  16000000),
(uuid_generate_v4(), 18, 2, '{"rooms":2,"floor_min":1,"floor_max":4,"district":"Заречный"}',        18000,    35000),
(uuid_generate_v4(), 19, 1, '{"rooms":3,"floor_min":2,"floor_max":10,"district":"Советский"}',      5000000,  8000000),
(uuid_generate_v4(), 20, 1, '{"rooms":1,"floor_min":1,"floor_max":7,"district":"Восточный"}',       1500000,  3000000),
(uuid_generate_v4(), 21, 2, '{"rooms":2,"floor_min":2,"floor_max":9,"district":"Центральный"}',     30000,    55000),
(uuid_generate_v4(), 22, 1, '{"rooms":3,"floor_min":3,"floor_max":14,"district":"Академический"}',  6500000,  11000000),
(uuid_generate_v4(), 23, 1, '{"rooms":2,"floor_min":1,"floor_max":8,"district":"Приморский"}',      4000000,  6500000),
(uuid_generate_v4(), 24, 1, '{"rooms":1,"floor_min":2,"floor_max":12,"district":"Северный"}',       2200000,  4200000);

INSERT INTO work."Transactions" (
    id, sellerClientID, buyerClientID, transactionTypeID, apartmentID,
    final_price, created_at, paid_at, canceled_at, terminated_at, termination_reason
)
SELECT
    uuid_generate_v4(),
    a.sellerID,
    buyer.clientID,
    1,
    a.id,
    a.priceTotal - (a.priceTotal * 0.02)::int,
    NOW() - (row_number() OVER (ORDER BY a.id) * interval '15 days'),
    NOW() - (row_number() OVER (ORDER BY a.id) * interval '10 days'),
    NULL,
    NULL,
    NULL
FROM apartments."Apartments" a
JOIN (
    VALUES (13),(14),(15),(16),(17),(18),(19),(20),(21),(22),(23),(24),(25),(13),(14)
) AS buyer(clientID) ON true
WHERE a.isAvailble = true
ORDER BY a.id
LIMIT 10;

INSERT INTO work."Transactions" (
    id, sellerClientID, buyerClientID, transactionTypeID, apartmentID,
    final_price, created_at, paid_at, canceled_at, terminated_at, termination_reason
)
SELECT
    uuid_generate_v4(),
    a.sellerID,
    20,
    1,
    a.id,
    a.priceTotal,
    NOW() - interval '60 days',
    NULL,
    NOW() - interval '55 days',
    NULL,
    'Покупатель отказался от сделки'
FROM apartments."Apartments" a
LIMIT 2;
 
INSERT INTO work."Transactions" (
    id, sellerClientID, buyerClientID, transactionTypeID, apartmentID,
    final_price, created_at, paid_at, canceled_at, terminated_at, termination_reason
)
SELECT
    uuid_generate_v4(),
    a.sellerID,
    21,
    1,
    a.id,
    a.priceTotal,
    NOW() - interval '90 days',
    NOW() - interval '85 days',
    NULL,
    NOW() - interval '30 days',
    'Выявлены нарушения при оформлении документов'
FROM apartments."Apartments" a
OFFSET 2 LIMIT 1;
 
