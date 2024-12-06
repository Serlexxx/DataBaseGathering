from DataBaseGathering import DataBaseGathering as DBG

from random import randint
from sys import maxsize
import datetime
import re

date_regex = re.compile(r'\d{4}-\d{2}-\d{2}')

db = DBG()


def default_start_menu(choice, target_user):
    if choice == 1:
        company_id = create_company(target_user)
    elif choice == 2:
        company_id = join_company(target_user)
    elif choice == 0:
        print("Выход из программы.")
        return None
    return company_id


def default_input_choice():
    return int(input("Выберите действие (введите номер): "))

# Самое главное меню
def menu_1(target_user):
    ind_menu = 0
    companies = is_user_in_any_company(target_user)
    if not companies is None:
        for company in companies:
            ind_menu += 1
            print(f"{ind_menu}. Компания '{company['name']}'")
    ind_menu += 1
    print(f"{ind_menu}. Создать компанию")
    ind_menu += 1
    print(f"{ind_menu}. Присоедениться к компании")
    print("0. Выход")

    choice = default_input_choice()

    if not companies is None:
        if choice > len(companies):
            choice -= len(companies)
        else:
            return companies[choice]['company_id']

    return default_start_menu(choice, target_user)

# Выбрали компанию
def menu_2(company_id):
    print("1. Добавить людей в компанию")
    print("2. Показать всех людей")
    print("3. Создать мероприятие")
    print("4. Редактировать мероприятие")
    print("0. Выход")

    choice = default_input_choice()

    if choice == 1:
        add_user_in_company(company_id, None)
    elif choice == 2:
        get_all_user_in_company(company_id)
    elif choice == 3:
        # TODO menu_3 создания
        create_gathering(company_id)
    # elif choice == 4:
        # TODO menu_4 редактирования
        # edit_gathering(company_id)
    elif choice == 0:
        print("Выход в главное меню.")
    else:
        print("Неверный выбор. Попробуйте снова.")
    return

def main_menu():
    ind_menu = 0
    company_id = 0
    target_user = authorization_user()

    while True:
        company_id = menu_1(target_user)
        if company_id is None:
            break
        menu_2(company_id)


def create_company(target_user):
    print("\n--- Добавление компании ---")
    name = input("Введите название компании: ")
    hex_company = hex(hash((randint(0, maxsize), name)))[2:]
    last_row = db.add_company(name, hex_company)
    print(f"Компания '{name}' добавлена.\nОтправьте hash своим друзьям: '{hex_company}'\n")
    add_user_in_company(last_row, target_user)
    return last_row


def authorization_user():
    print("\n--- Авторизация user ---")
    user_name = input("Введите имя: ")
    user_tag = input("Введите tg tag: ")
    print("\n--- Поиск user в бд ---")
    user = db.find_person(user_tag)
    return {'person_id': None, 'person_name': user_name, 'tg_tag': user_tag} if user is None else user


def is_user_in_any_company(user):
    if user['person_id'] is None:
        return None

    return db.find_person_in_any_company(user['person_id'])


def add_user_in_company(company_id, target_user):
    if target_user is None:
        # Добавляем другого человека
        user_name = input("Введите имя: ")
        user_tag = input("Введите tg tag: ")
    else:
        # Добавлем себя в созданную компанию или куда присоеденились
        user_name = target_user['person_name']
        user_tag = target_user['tg_tag']

    print("\n--- Поиск user в бд ---")
    user = db.find_person(user_tag)
    if user is None:
        print("\n--- Не нашли, регистрируем user в бд ---")
        db.add_person_and_link_to_company(company_id, user_name, user_tag)
    else:
        print("\n--- Нашли, присоеденили ---")
        db.add_person_to_company(company_id, user['person_id'])


def get_all_user_in_company(company_id):
    ind = 0
    for user in db.get_all_user_in_company(company_id):
        ind += 1
        print(f"{ind}. {user['person_name']} ({user['tg_tag']})")


def join_company(target_user):
    print("\n--- Поиск компании ---")
    hex_company = input("Введите hash компании: ")
    company = db.find_company(hex_company)
    if company is None:
        print(f"Компания с таким hash '{hex_company}' не существует. Попробуйте снова\n")
        return 0
    else:
        print(f"Присоединяемся к компании: '{company['name']}'\n")
        add_user_in_company(company['company_id'], target_user)
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
