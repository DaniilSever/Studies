import pandas as pd
from datetime import datetime


def time(result_data):
    start_index = result_data.loc[result_data['Статус'] == 'start'].index
    finish_index = result_data.loc[result_data['Статус'] == 'finish'].index
    reslist = []

    for i in range(0, len(start_index)):
        start = datetime.strptime(result_data['Время'].loc[start_index[i]], '%H:%M:%S')
        end = datetime.strptime(result_data['Время'].loc[finish_index[i]], '%H:%M:%S')
        result = end - start
        reslist.append(result)

    temp = pd.DataFrame(list(reslist), columns=['Итоговое время'])
    return temp


def main():
    # Загрузка файлов
    main_data = pd.read_json("./src/competitors2.json").T.reset_index()
    result_data = pd.read_table("./src/results_RUN.txt", sep=' ', header=None)

    # Переименование колонок
    main_data.columns = ['Нагрудный номер', 'Имя', 'Фамилия']
    result_data.columns = ['Нагрудный номер', 'Статус', 'Время']
    result_data['Время'] = result_data['Время'].str.split(',').str.get(0)
    result_data = result_data.reset_index(drop='index')

    time_data = time(result_data)

    result_data.drop(result_data.loc[result_data['Статус'] == 'start'].index, inplace=True)
    result_data = result_data.reset_index(drop='index')
    result_data = result_data.join(time_data)

    del result_data['Статус']
    del result_data['Время']

    finish_data = main_data.merge(result_data, on='Нагрудный номер', how='left')

    finish_data['Итоговое время'] = finish_data['Итоговое время'].astype('string')
    finish_data['Итоговое время'] = finish_data['Итоговое время'].str.split(' ').str.get(2)

    finish_data = finish_data.sort_values(by='Итоговое время', ascending=True)
    finish_data = finish_data.reset_index(drop='index')

    print(finish_data)


if __name__ == "__main__":
    main()
