import json
import os
from abc import ABC, abstractmethod

import requests


class Saver(ABC):
    """Абстрактный класс для сохранения вакансий в файл."""
    json_file = 'config/vacancies.json'
    # csv_file = ''
    # txt_file = ''

    @abstractmethod
    def to_json(self, json_file, vacancies):
        pass

    @staticmethod
    def check_file(json_file) -> None:
        if not os.path.exists(json_file):
            raise FileNotFoundError("JSON файл с вакансиями не найден")


class JSONSaver(Saver):
    """Класс для сохранения вакансий в JSON формате."""
    __slots__ = ()

    def to_json(self, json_file, vacancies):
        print(self.json_file)


class Vacancy:
    """Класс для работы с вакансиями."""
    __slots__ = ('vacancy_id', 'name', 'salary', 'vacancy_url', 'description')

    collected_vacancies = []

    def __init__(self, vacancy_id: int, name: str, salary: str | dict, vacancy_url: str, description: str):
        self.vacancy_id = vacancy_id
        self.name = name
        self.salary = self.__get_user_salary(salary)
        self.vacancy_url = vacancy_url
        self.description = description

    @staticmethod
    def __get_user_salary(salary: str | dict) -> dict:
        """Получает зарплату в виде "от до валюта" и возвращает в виде словаря."""
        if isinstance(salary, dict):
            return salary
        salary = salary.split()
        salary_dict = {
            "from": salary[0],
            "to": salary[1],
            "currency": salary[2].upper(),
        }
        return salary_dict

    def add_user_vacancy(self):
        """Метод для добавления пользовательской вакансии основной список вакансий"""
        vacancy = {"id": self.vacancy_id,
                   "name": self.name,
                   "salary": self.salary,
                   "vacancy_url": self.vacancy_url,
                   "description": self.description,
                   }
        self.collected_vacancies.append(vacancy)

    def get_vacancy_info(self):
        vacancy_info = ('------------------\n'
                        f'ID вакансии: {self.vacancy_id}\n'
                        f'Наименование вакансии: {self.name}\n'
                        'Зарплата: \n'
                        f'\tот: {self.salary["from"]}\n'
                        f'\tдо: {self.salary["to"]}\n'
                        f'\tвалюта: {self.salary["currency"]}\n'
                        f'Ссылка: {self.vacancy_url}\n'
                        f'Описание: {self.description}')
        return vacancy_info

    def __str__(self):
        # принт вакансии
        vacancy_info = ('------------------\n'
                        f'ID вакансии: {self.vacancy_id}\n'
                        f'Наименование вакансии: {self.name}\n')
        return vacancy_info

    def __repr__(self):
        return (f'{self.__class__.__name__}({self.vacancy_id=}, {self.name=}, '
                f'{self.salary=}, {self.vacancy_url=}, {self.description=})')


class APIVacancy(ABC):
    """Абстрактный класс для работы с API сайтов с вакансиями."""
    __slots__ = ()

    @abstractmethod
    def get_vacancies(self, *args) -> None:
        pass


class HeadHunterAPI(APIVacancy, Vacancy):
    """Класс для работы с вакансиями сайта HH.ru посредством API."""
    __slots__ = ()

    def __init__(self) -> None:
        pass

    def get_vacancies(self, query: str) -> list:

        # проходим в цикле по страницам результата запроса (100 записей на 1 страницу)
        for page in range(0, 1):
            new_data = json.loads(self.__get_page(query, page))

            # проверка на 2000 записей при 100 записях на 1 странице
            # если кол-во страниц результата запроса равно значению "page"
            # выходим из цикла
            if new_data['pages'] == page:
                break

            for vacancy in new_data['items']:
                vacancy_id = int(vacancy["id"])
                name = vacancy["name"]
                salary = self.__get_hh_salary(vacancy)
                vacancy_url = vacancy["alternate_url"]
                description = self.__get_hh_description(vacancy)
                vacancy = Vacancy(vacancy_id, name, salary, vacancy_url, description)

                self.collected_vacancies.append(vacancy)

        return self.collected_vacancies

    @staticmethod
    def __get_page(query: str, page: int) -> str:
        """Функция получает данные по вакансиям с необходимой страницы для дальнейшей работы."""
        params = {
            'text': f'NAME:{query}',
            'page': page,
            'per_page': 10,
        }

        req = requests.get('https://api.hh.ru/vacancies', params)
        data = req.content.decode()  # декодируем
        return data

    @staticmethod
    def __get_hh_salary(vacancy: dict) -> str | dict:
        """Метод для записи зарплаты в JSON по шаблону."""
        if vacancy["salary"]:
            if vacancy["salary"]["from"]:
                salary_from = vacancy["salary"]["from"]
            else:
                salary_from = 0

            if vacancy["salary"]["to"]:
                salary_to = vacancy["salary"]["to"]
            else:
                salary_to = 0

            if vacancy["salary"]["currency"] == "RUR":
                currency = "RUB"
            else:
                currency = vacancy["salary"]["currency"]

        else:
            return 'Не указана'

        salary = {"from": salary_from,
                  "to": salary_to,
                  "currency": currency, }

        return salary

    @staticmethod
    def __get_hh_description(vacancy: dict) -> str:
        """Возвращает требования к вакансии, если они есть."""
        if vacancy["snippet"]["requirement"]:
            return f'{vacancy["snippet"]["requirement"]}'
        return 'Не указано'


class SuperJobAPI(APIVacancy, Vacancy):
    """Класс для работы с вакансиями сайта superjob.ru посредством API."""
    __slots__ = ()

    secret_key = os.getenv('sj_key')

    def __init__(self) -> None:
        pass

    def get_vacancies(self, query: str) -> list:

        # проходим в цикле по страницам результата запроса (100 записей на 1
        # страницу)
        for page in range(0, 1):
            new_data = json.loads(self.__get_page(query, page))

            # список для форматированных вакансий
            formatted_vacancies = []
            for vacancy in new_data['objects']:
                vacancy_id = int(vacancy["id"])
                name = vacancy["profession"]
                salary = self.__get_sj_salary(vacancy)
                vacancy_url = vacancy["link"]
                description = vacancy["candidat"]
                vacancy = Vacancy(vacancy_id, name, salary, vacancy_url, description)
                self.collected_vacancies.append(vacancy)

        return self.collected_vacancies

    @staticmethod
    def __get_page(query: str, page: int) -> str:
        """Функция получает JSON данные по вакансиям с необходимой страницы для дальнейшей работы."""
        headers = {'Host': 'api.superjob.ru',
                   'X-Api-App-Id': SuperJobAPI.secret_key, }
        params = {'keyword': query,
                  'page': page,
                  'count': 10}

        req = requests.get('https://api.superjob.ru/2.0/vacancies/',
                           headers=headers, params=params)
        data = req.content.decode()  # декодируем
        return data

    @staticmethod
    def __get_sj_salary(vacancy: dict) -> str | dict:
        """Метод для записи зарплаты в JSON по шаблону."""
        salary_from = vacancy["payment_from"]
        salary_to = vacancy["payment_to"]
        currency = vacancy["currency"].upper()

        if salary_from == 0 and salary_to == 0:
            return 'Не указана'

        salary = {"from": salary_from,
                  "to": salary_to,
                  "currency": currency, }

        return salary
