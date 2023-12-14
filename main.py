import requests
import geocoder
import json
from datetime import datetime, timezone, timedelta

API_KEY = "112c09ae6fba0e4ea0d3c32abeb3840d"


def data_preprocessing(data: dict) -> dict:
    """
    Функция получает из API словарь с параметрам, форматирует их  нужным образом.
    in: data - словварь из API
    out: processed_data - обработанный словарь только с необходимыми данными
    """
    # Получаем timestamp в UTC (секунды с 1 января 1970)
    timestamp = data["dt"]
    # Получаем сдвиг временной зоны от UTC в секундах
    timezone_shift = data["timezone"]
    # Получаем таймзону
    loc_timezone = timezone(timedelta(seconds=timezone_shift))
    # форматируем время от timestamp в нужной таймзоне
    loc_time = datetime.fromtimestamp(timestamp, loc_timezone)
    # Получаем необходимые параметры
    weather_cond = data['weather'][0]['description']
    city_name = data['name']
    current_temp = data['main']['temp']
    feels_temp = data['main']['feels_like']
    wind_vel = data['wind']['speed']
    # Создаем словарь с нужными свойствами
    processed_data = {'loc_time': str(loc_time),
                      'city_name': str(city_name),
                      "weather_cond": str(weather_cond),
                      'current_temp': str(current_temp),
                      'feels_temp': str(feels_temp),
                      'wind_vel': str(wind_vel)}
    return processed_data


def save_to_file(data: dict):
    """
    Функция получает словарь с данными и добавляет к сохраненным данным в файле "data.json"
    in: data - словарь с новыми данными
    """
    # Получаем список словарей из файла сохранения
    current_dataset = read_file()
    # Проверяем что он не пустой
    if current_dataset is None:
        current_dataset = []
    # Добавляем новые данные
    current_dataset.append(data)
    json_data = json.dumps(current_dataset, indent=1, ensure_ascii=False)
    with open("data.json", "w+") as file:
        file.write(json_data)


def clear_history():
    """
    Функция ощищает историю, т.е. перезаписывает файл сохранения на пустой
    """
    with open("data.json", "w+") as file:
        file.write("")
    print("История успешно очищена!")


def read_file() -> list:
    """
    Функция читает data.json и возвращает список из словарей предыдущих вызовов
    """
    try:
        with open("data.json", "r+") as file:
            data = json.load(file)
        return data
    except:
        pass


def print_history(num_of_requests: str):
    """
    Функция выводит num_of_requests последних вызовов
    in: num_of_requests - количество выводимых последних вызовов
    """
    # Проверка на целочисленные значения
    try:
        num_of_requests = int(num_of_requests)
    except:
        print("Введите целочисленное значение >0!")
        return
    # Проверка положительности количества выводимых последних вызовов
    if num_of_requests <= 0:
        print("Введите целочисленное значение >0!")
        return
    data = read_file()
    if data is None:
        print("Нет записей!")
        return
    actual_size = len(data)
    # Если запрашивааемое число выводов больше количетсва сохраненных, выведется максимально доступное
    if num_of_requests > actual_size:
        num_of_requests = actual_size
    # Вывод поштучно истории с нумерацией
    reversed_data = data[::-1]
    for i in range(num_of_requests):
        print(i + 1, "-" * 30)
        print_weather(reversed_data[i])


def print_weather(data: dict):
    """
    Отображение погоды в нужном формате
    in: data - словарь с данными
    """
    print("Текущее время: ", data['loc_time'])
    print("Название города: ", data['city_name'])
    print("Погодные условия: ", data['weather_cond'])
    print("Текущая температура: ", data['current_temp'], ' градусов цельсия')
    print("Ощущается как: ", data['feels_temp'], ' градусов цельсия')
    print("Скорость ветра: ", data['wind_vel'], ' м/с')


def get_data_by_name(city_name: str):
    """
    Получение погоды по названию города
    in: city_name: название города
    """
    try:
        # Посылаем запрос
        url_scheme = f"https://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={API_KEY}&units=metric&lang=ru"
        request = requests.get(url_scheme)
        # Вызов проверки ошибки
        request.raise_for_status()
        # Получаем данные в json
        weather_data = request.json()
        # обрабатываем json
        weather_processed_data = data_preprocessing(weather_data)
        # Отображаем данные
        print_weather(weather_processed_data)
        # Сохраняем данные
        save_to_file(weather_processed_data)
    except requests.exceptions.HTTPError:
        print(f"Город не найден!")
    except requests.exceptions.RequestException as err:
        print(f"Request exception occurred: {err}")


def get_data_by_loc():
    """
    Получение погоды по текущей геололкации
    """
    try:
        # Получаем по геолокации название города
        my_loc = geocoder.ip("me").city
        # вызываем функцию получения погоды по городу
        get_data_by_name(my_loc)
    except requests.exceptions.HTTPError:
        print(f"Город не найден!")
    except requests.exceptions.RequestException as err:
        print(f"Request exception occurred: {err}")


def input_formatter(user_input: str) -> str:
    """
    Обработка вводимых пользователем занчений.
    Убираются проверки.
    Уираются заглавные буквы
    in: user_input - строка от пользователя
    out: formatted_input - отформатированная строка
    """
    formatted_input = user_input.replace(" ", "")
    formatted_input = formatted_input.lower()
    return formatted_input


def show_commands():
    """
    Отображение подсказки допустимых комманд
    """
    command_list = {'help': 'вызов подсказки',
                    'name': 'погода по названию города',
                    'loc': 'погода по текущей локации',
                    'hist': 'история последених запросов',
                    'clr': 'очистить историю запросов',
                    'exit': 'выход'}
    keys = command_list.keys()
    print('\n Подсказка:')
    for key in keys:
        print(key, ' - ', command_list[key])


def main():
    """
    Обработка вводимых пользователем комманд и вызов соответсвующих функций.
    При запуске выводится подсказка с командами:
    'help': 'вызов подсказки',
    'name': 'погода по названию города',
    'loc': 'погода по текущей локации',
    'hist': 'история последних запросов',
    'clr': 'очистить историю запросов',
    'exit': 'выход'
    """
    show_commands()
    while True:
        user_input = input("\nВведите команду:")
        formatted_input = input_formatter(user_input)
        if formatted_input == 'name':
            city_name = input("Введите название города:")
            city_name = input_formatter(city_name)
            get_data_by_name(city_name)
        elif formatted_input == 'help':
            show_commands()
        elif formatted_input == 'loc':
            get_data_by_loc()
            pass
        elif formatted_input == 'hist':
            user_input = input("Введите желаемое количество отображенных запросов:")
            formatted_input = input_formatter(user_input)
            print_history(formatted_input)
        elif formatted_input == 'clr':
            clear_history()
        elif formatted_input == 'exit':
            break
        else:
            print("Команда не распознана. Проверьте корректность ввода.")


if __name__ == '__main__':
    main()
