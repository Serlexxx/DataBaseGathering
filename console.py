from DataBaseGathering import DataBaseGathering as DBG

from random import randint
from sys import maxsize
import datetime
import re

date_regex = re.compile(r'\d{4}-\d{2}-\d{2}')

db = DBG()


def main_menu():
    company_id = 0
    while True:
        print("\nГлавное меню:")
        if company_id == 0:
            print("1. Создать компанию")
            print("2. Присоедениться к компании")
            print("0. Выход")

            choice = input("Выберите действие (введите номер): ")

            if choice == "1":
                company_id = create_company()
            elif choice == "2":
                company_id = join_company()
            elif choice == "0":
                print("Выход из программы.")
                break
            else:
                print("Неверный выбор. Попробуйте снова.")

            if company_id != 0:
                # Вставляет каждый раз новую запись, в боте не должно быть такого
                # TODO добавить выбор компании в которых я есть
                add_user_in_company(company_id)
        else:
            print("1. Добавить людей в компанию")
            print("2. Создать мероприятие")
            print("3. Редактировать мероприятие")
            print("0. Выход")

            choice = input("Выберите действие (введите номер): ")

            if choice == "1":
                add_user_in_company(company_id)
            elif choice == "2":
                create_gathering(company_id)
            # elif choice == "3":
                # TODO
                # edit_gathering(company_id)
            elif choice == "0":
                print("Выход из программы.")
                break
            else:
                print("Неверный выбор. Попробуйте снова.")
            return


def create_company():
    print("\n--- Добавление компании ---")
    name = input("Введите название компании: ")
    hex_company = hex(hash((randint(0, maxsize), name)))[2:]
    last_row = db.add_company(name, hex_company)
    print(f"Компания '{name}' добавлена.\nОтправьте hash своим друзьям: '{hex_company}'\n")
    return last_row


def add_user_in_company(company_id):
    # В боте автоматом получаем при переходе в этот сценарий
    user_name = input("Введите имя: ")
    user_tag = input("Введите tg tag: ")
    print("\n--- Поиск user в бд ---")
    user = db.find_person(user_tag)
    if user is None:
        print("\n--- Не нашли, регистрируем добавить user в бд ---")
        db.add_person_and_link_to_company(company_id, user_name, user_tag)
    else:
        print("\n--- Нашли, присоеденили ---")
        db.add_person_to_company(company_id, user['person_id'])


def join_company():
    print("\n--- Поиск компании ---")
    hex_company = input("Введите hash компании: ")
    company = db.find_company(hex_company)
    if company is None:
        print(f"Компания с таким hash '{hex_company}' не существует. Попробуйте снова\n")
        return 0
    else:
        print(f"Присоединяемся к компании: '{company['name']}'\n")
        return company['company_id']

def create_gathering(company_id):
    print("\n--- Создаем мероприятие ---")
    date = datetime.date.today().isoformat()
    # inline ввод Да/Нет в боте
    today = input("Мероприятие было сегодня?(Да/Нет): ")
    if today == "Нет":
        while True:
            date = input("Введите дату в формате YYYY-MM-DD:\t")
            if re.match(date_regex, date):
                break
            else:
                print("Sorry not sorry\n")
    locate = input("Введите название места:")
    gathering_id = db.add_gathering(date, locate, company_id)
    # TODO добавление позиций или атомарное мероприятие и позиции

if __name__ == "__main__":
    main_menu()
