import json
import os
from abc import ABC, abstractmethod

import requests


class MixinVacanciesStorage:
    """Класс для сбора вакансий в списке."""
    collected_vacancies = []
    vacancies_count = len(collected_vacancies)


class Saver(ABC):
    """Абстрактный класс для сохранения вакансий в файл."""
    json_file = 'data/vacancies.json'

    # csv_file = ''
    # txt_file = ''

    @abstractmethod
    def to_json(self, json_file):
        pass

    @staticmethod
    def check_file(json_file) -> None:
        if not os.path.exists(json_file):
            raise FileNotFoundError("JSON файл с вакансиями не найден")


class JSONSaver(Saver, MixinVacanciesStorage):
    """Класс для сохранения вакансий в JSON формате."""
    __slots__ = ()

    def to_json(self, vacancies: list) -> None:
        """Метод добавления вакансий в JSON файл"""
        with open(self.json_file, 'r', encoding='utf-8') as f:
            vacancies_list = json.load(f)
            for vacancy in vacancies:
                vacancy = {"id": vacancy.vacancy_id,
                           "name": vacancy.name,
                           "salary": vacancy.salary,
                           "vacancy_url": vacancy.vacancy_url,
                           "description": vacancy.description,
                           }

                vacancies_list.append(vacancy)

            with open(self.json_file, 'w', encoding='utf-8') as outfile:
                json.dump(vacancies_list, outfile, ensure_ascii=False, indent=2)
        print("-----------------\n"
              "Найденные вакансии сохранены")


class Vacancy(MixinVacanciesStorage):
    """Класс для работы с вакансиями."""
    __slots__ = ('vacancy_id', 'name', 'salary', 'vacancy_url', 'description')

    def __init__(self, vacancy_id: int, name: str, salary: str | dict, vacancy_url: str, description: str):
        if self.__check_values(vacancy_id, name, salary, vacancy_url, description):
            self.vacancy_id = vacancy_id
            self.name = name
            self.salary = self.__get_salary(salary)
            self.vacancy_url = vacancy_url
            self.description = description

    @classmethod
    def __check_values(cls, vacancy_id: int, profession: str, salary: dict | str, vacancy_url: str,
                       description: str) -> bool:
        """Метод класса для возбуждения исключений при неверных входных данных."""
        if not isinstance(vacancy_id, int):
            raise TypeError("ID Вакансии должен состоять из цифр")
        if not len(str(vacancy_id)) == 8:
            raise ValueError("Длина ID вакансии должно быть равным 8 (восьми)")
        if not len(profession) >= 10:
            raise TypeError("Наименование вакансии должно состоять из минимум 10 символов.")
        # if isinstance(salary, dict):
        #     if not salary["from"] or not salary["to"] or not salary["currency"]:
        #         raise KeyError("Не указано значение зарплаты ОТ, ДО или ВАЛЮТА")
        if isinstance(salary, int):
            raise "Зарплата ОТ, ДО и Валюта должны быть разделены пробелами (всего два пробела)"
        elif salary != "Не указана" and not isinstance(salary, dict):
            salary_split = salary.split()
            if len(salary_split) != 3:
                raise "Зарплата ОТ, ДО и Валюта должны быть разделены пробелами (всего два пробела)"
            elif not int(salary_split[1]) >= int(salary_split[0]):
                raise "Зарплата ДО должна быть больше или равна зарплате ОТ"
            elif len(salary_split[2]) != 3:
                raise "Наименование валюты должно состоять из 3 букв"

        if not vacancy_url.startswith("https://"):
            raise "Ссылка должна начинаться с https://"
        # elif not vacancy_url.endswith(".ru"):
        #     raise "Ссылка должна заканчиваться на .ru"
        if not len(description) >= 10:
            raise TypeError("Описание должно состоять минимум из 10 символов")

        return True

    @staticmethod
    def __get_salary(salary: str | dict) -> str | dict:
        """Получает зарплату в виде "от до валюта", "не указана" или словаря и возвращает в виде словаря."""
        if isinstance(salary, dict):
            return salary
        elif salary != "Не указана":
            salary_from, salary_to, currency = salary.split()
            salary_dict = {
                "from": salary_from,
                "to": salary_to,
                "currency": currency.upper(),
            }
            return salary_dict
        else:
            return salary

    def add_vacancy(self):
        """Метод для добавления пользовательской вакансии в список вакансий"""
        # vacancy = {"id": self.vacancy_id,
        #            "name": self.name,
        #            "salary": self.salary,
        #            "vacancy_url": self.vacancy_url,
        #            "description": self.description,
        #            }
        self.collected_vacancies.append(self)

    def get_salary_for_print(self):
        """Для печати зарплаты в необходимом виде."""
        if isinstance(self.salary, dict):
            salary = (f'\tот: {self.salary["from"]}\n'
                      f'\tдо: {self.salary["to"]}\n'
                      f'\tвалюта: {self.salary["currency"]}')
            return salary
        return f"\t{self.salary}"

    def __str__(self):
        # принт вакансии
        vacancy_info = ('------------------\n'
                        f'ID вакансии: {self.vacancy_id}\n'
                        f'Наименование вакансии: {self.name}\n'
                        f'Зарплата: \n{self.get_salary_for_print()}\n'
                        f'Ссылка: {self.vacancy_url}\n'
                        f'Описание: {self.description}')
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


class HeadHunterAPI(APIVacancy, MixinVacanciesStorage):
    __slots__ = ()

    def get_vacancies(self, query: str) -> list:
        print("Идет процесс сбора вакансий...")

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
            'per_page': 30,
        }

        req = requests.get('https://api.hh.ru/vacancies', params)
        data = req.content.decode()  # декодируем
        return data

    @staticmethod
    def __get_hh_salary(vacancy: dict) -> str | dict:
        """Возвращает зарплату по шаблону."""
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


class SuperJobAPI(APIVacancy, MixinVacanciesStorage):
    """Класс для работы с вакансиями сайта superjob.ru посредством API."""
    __slots__ = ()
    secret_key = os.getenv('sj_key')

    def get_vacancies(self, query: str) -> list:
        print("Идет процесс сбора вакансий...")

        # проходим в цикле по страницам результата запроса (100 записей на 1
        # страницу)
        for page in range(0, 5):
            new_data = json.loads(self.__get_page(query, page))

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
                  'count': 100}

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
