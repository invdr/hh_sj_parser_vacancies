from typing import List

from config.classes import *


def get_platform() -> HeadHunterAPI | SuperJobAPI:
    """Выбор платформы поиска вакансий."""
    platforms = (HeadHunterAPI(), SuperJobAPI())
    print("-----------------\n"
          "1. HeadHunter\n2. SuperJob\n"
          "-----------------")

    while True:
        platform_choice = input("Введите номер платформы (1 или 2): ")
        if platform_choice.isdigit() and int(platform_choice) in (1, 2):
            platform_choice = int(platform_choice)
            break
    # создаем объект для работы с API
    if platform_choice == 1:
        return platforms[0]
    return platforms[1]


def get_user_choice(vacancies: List[Vacancy]):
    print("------------------\n"
          "Доступные действия:\n"
          "1. Показать все собранные вакансии\n"
          "2. Показать вакансию по ID\n"
          "3. Показать топ N вакансий\n"
          # "4. Сортировать по наличию зарплаты в вакансии\n"
          # "5. Удалить вакансию из собранных по его ID\n"
          # "6. Добавить вакансию в список" # Vacancy.
          # "7. - показать все добавленные вакансии\n"
          # "8. - удалить последнюю добавленную вакансию"
          )
    print("0. Выход\n")

    user_move = ''
    while not user_move.isdigit():
        user_move = input("Выберите действие (номер действия): ")

    user_move = int(user_move)

    while True:
        if user_move == 1:
            for vac in vacancies:
                print(vac)
            get_user_choice(vacancies)
        elif user_move == 2:
            user_id = check_id()
            for vac in vacancies:
                if vac.vacancy_id == user_id:
                    print(vac)
            get_user_choice(vacancies)

        elif user_move == 3:
            top_n = int(input("Введите топ N: "))
            for index, vac in enumerate(vacancies):
                print(vac)
                if index == top_n - 1:
                    break
            get_user_choice(vacancies)

        elif user_move == 4:
            user_choice = int(input("Выберите дальнейшее действие с выбранной вакансией: "))

        elif user_move == 0:
            print("Спасибо")
            break
        else:
            print("Неверный выбор")
            break


if __name__ == '__main__':
    # get_user_choice(vacancies=Vacancy())
    pass


def check_id():
    user_id = ''
    while not user_id.isdigit():
        user_id = input("Введите ID вакансии: ")
    return int(user_id)
