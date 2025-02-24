import json
import asyncio
from pathlib import Path
from collections import defaultdict
from datetime import datetime, timedelta


# ---------- Const ----------
BASE_DIR = Path(__file__).parent
FILE_DIR = BASE_DIR / "data"
RESULT_DIR = BASE_DIR / "result"
RACE_FILE = "race_data.json"
FILE_PRIZES = {
    "M15": "prizes_list_m15.txt",
    "M16": "prizes_list_m16.txt",
    "M18": "prizes_list_m18.txt",
    "W15": "prizes_list_w15.txt",
    "W16": "prizes_list_w16.txt",
    "W18": "prizes_list_w18.txt",
}
# ---------------------------


async def get_prize_data(file_name: str) -> dict[str, str]:
    """Считывает данные из файла с призами и возвращает их в виде словаря.

    Args:
        file_name (str): Имя файла с данными о призах.

    Returns:
        dict[str, str]: Словарь, где ключ — место участника, значение — соответствующий приз.
    """
    prizes = {}
    with open(FILE_DIR / file_name) as f:
        for line in f.readlines():
            line = line.replace("\n", "")
            line = line.split(" место ")

            prizes[line[0]] = line[1]

    return prizes


async def get_race_data(file_name: str) -> dict[str, list[dict[str, any]]]:
    """Считывает данные о забеге из JSON-файла и группирует их по категориям.

    Args:
        file_name (str): Имя JSON-файла с данными о забеге.

    Returns:
        dict[str, list[dict[str, any]]]: Словарь, где ключ — категория забега, а значение — список данных участников.
    """
    race = {}
    with open(FILE_DIR / file_name) as f:
        race_data = json.load(f)
        for data in race_data:
            category = data.pop("Категория")
            if category not in race:
                race[category] = []
            race[category].append(data)

    return race


async def create_result(race: list[dict[str, any]], prizes: dict[str, str]) -> list[dict[str, any]]:
    """Создает итоговый список результатов забега, рассчитывая время и распределяя призы.

    Args:
        race (list[dict[str, any]]): Список данных участников забега.
        prizes (dict[str, str]): Словарь с распределением призов по местам.

    Returns:
        list[dict[str, any]]: Отсортированный список результатов с указанием места, времени прохождения дистанции и присвоенными призами.
    """
    pre_result = []
    for res in race:
        first_name = res.pop("Имя")
        last_name = res.pop("Фамилия")
        start_time = datetime.strptime(res.pop("Время старта"), "%H:%M:%S")
        finish_time = datetime.strptime(res.pop("Время финиша"), "%H:%M:%S")
        res["Имя и Фамилия"] = f"{first_name} {last_name}"

        if finish_time <= start_time:
            finish_time += timedelta(days=1)

        res["Время"] = str(finish_time - start_time)
        pre_result.append(res)

    sorted_data = sorted(
        pre_result,
        key=lambda x: datetime.strptime(x["Время"], "%H:%M:%S"),
    )

    grouped_data = defaultdict(list)

    for item in sorted_data:
        grouped_data[item["Время"]].append(item)

    unique_data = []
    for _, items in grouped_data.items():
        min_item = min(items, key=lambda x: x["Нагрудный номер"])
        unique_data.append(min_item)

    results = []
    for position, item in enumerate(unique_data, start=1):
        item["Место"] = position
        if position < 50:
            item["Приз"] = prizes.get(str(position))
        results.append(item)

    return results


async def create_and_save_results(category: str, race_list: list[dict[str, any]], prizes: dict[str, str]):
    """Создает результаты забега для указанной категории и сохраняет их в JSON-файл.

    Args:
        category (str): Категория забега.
        race_list (list[dict[str, any]]): Список данных участников забега в данной категории.
        prizes (dict[str, str]): Словарь с распределением призов по местам.
    """
    result = await create_result(race_list, prizes)
    with open(RESULT_DIR / f"{category}.json", "w") as f:
        json.dump(result, f, ensure_ascii=False, indent=4)


async def preparation_execution():
    """Подготавливает данные для выполнения и сохраняет результаты забегов по категориям.

    Считывает данные о призах и участниках, затем для каждой категории запускает процесс создания и сохранения результатов.
    """
    prizes_by_categories = {
        category: await get_prize_data(file)
        for category, file in FILE_PRIZES.items()
    }
    race = await get_race_data(RACE_FILE)

    tasks = [
        create_and_save_results(category, race_list, prizes_by_categories[category])
        for category, race_list in race.items()
    ]
    await asyncio.gather(*tasks)


def main():
    """Основная функция, запускающая асинхронное выполнение подготовки и сохранения результатов.

    Проверяет, если уже существует активный цикл событий, то выполняет подготовку в рамках этого цикла,
    иначе запускает новый цикл с помощью asyncio.run.
    """
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None

    if loop and loop.is_running():
        return asyncio.ensure_future(preparation_execution())

    asyncio.run(preparation_execution())


if __name__ == "__main__":
    main()
