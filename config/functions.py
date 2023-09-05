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
