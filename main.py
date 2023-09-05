import pprint

from config.classes import *
from config.functions import *


def main():
    user_input = input('Введите ваш запрос: ')
    working_api = get_platform()
    working_api.get_vacancies(user_input)
    print("Всего найдено ", len(working_api.collected_vacancies), "вакансий")


def user_():
    vacancy = Vacancy(11111111, "Python джуниор", "100000 200000 руб", "https://python.ru",
                      "Вакансия для джуниора. Требования: Python, SQL, Django 4")
    vacancy2 = Vacancy(11111112, "Python middle", "150000 200000 руб", "https://python.ru",
                       "Вакансия для middle. Требования: Python, SQL, Django 4")
    vacancy3 = Vacancy(11111113, "Python senior", "200000 250000 руб", "https://python.ru",
                       "Вакансия для Senior. Требования: Python, SQL, Django 4")

    vacancy.add_user_vacancy()
    print(vacancy.get_vacancy_info())


if __name__ == '__main__':
    main()
