import pprint

from config.classes import *
from config.functions import *


def main():
    user_input = input('Введите ваш запрос: ')
    working_api = get_platform()
    vacancies = working_api.get_vacancies(user_input)

    # сохранение вакансий в файл
    saver = JSONSaver()
    saver.to_json(vacancies)
    print("Найденные вакансии сохранены")
    print("Всего найдено", len(vacancies), "вакансий")

    # показать все собранные вакансии
    # for vac in vacancies:
    #     print(vac)


def user_():

    vacancy = Vacancy(11111111, "Python джуниор", "Не указана", "https://python.ru",
                      "Вакансия для джуниора. Требования: Python, SQL, Django 4").add_vacancy()
    vacancy2 = Vacancy(11111112, "Python middle", "150000 200000 руб", "https://python.ru",
                       "Вакансия для middle. Требования: Python, SQL, Django 4").add_vacancy()
    vacancy3 = Vacancy(11111113, "Python senior", "200000 250000 руб", "https://python.ru",
                       "Вакансия для Senior. Требования: Python, SQL, Django 4").add_vacancy()

    vacancies = Vacancy.collected_vacancies
    # сохранение вакансий в файл
    saver = JSONSaver()
    saver.to_json(vacancies)
    print("Добавленные вакансии сохранены")
    print("Добавлено всего", len(vacancies), "вакансий")
    for vac in vacancies:
        print(vac)


if __name__ == '__main__':
    user_()
