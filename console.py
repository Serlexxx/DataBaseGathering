from DataBaseGathering import DataBaseGathering as DBG

from random import randint
from sys import maxsize
import datetime
import re
from collections import Counter

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
        elif choice != 0:
            return companies[choice - 1]['company_id']

    return default_start_menu(choice, target_user)


# Выбрали компанию
def menu_2(company_id):
    print("1. Добавить людей в компанию")
    print("2. Показать всех людей")
    print("3. Создать мероприятие")
    print("4. Редактировать мероприятие")
    print("5. Показать список мероприятий")
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
    # elif choice == 5:
    # TODO menu_5 вывод списка мероприятий
    # edit_gathering(company_id)
    elif choice == 0:
        print("Выход в главное меню.")
        return None
    else:
        print("Неверный выбор. Попробуйте снова.")
    return company_id


def main_menu():
    company_id = None
    target_user = authorization_user()

    while True:
        if company_id is None:
            company_id = menu_1(target_user)
        if company_id is None:
            break
        company_id = menu_2(company_id)


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
    print("\n")


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


def adding_receipt_positions(company_id, gathering_id):
    print("\n--- Заполняем чеки ---")
    ind = 0
    receipt_positions = []
    groups = []

    # Получаем всех людей для формирования групп и выбора кто платил за позицию в чеке
    users = db.get_all_user_in_company(company_id)

    while True:
        group = []
        description = input("Введите позицию чека: ")
        # TODO Добавить проверку, что это float
        amount = input("Введите цену позиции чека: ")

        for user in users:
            ind += 1
            print(f"{ind}. {user['person_name']} ({user['tg_tag']})")
        ind = 0

        # TODO Добавить проверку, что это int > 0
        choice_payed_person_id = int(input("Кто платил за позицию: ")) - 1
        payed_person_id = users[choice_payed_person_id]['person_id']

        # Собираем кто заказывал эту позицию
        while True:
            choice_person = int(input("Кто заказывал?: (0 - закончить, -1 - общак): "))
            if choice_person == 0:
                break
            if choice_person == -1:
                for user in users:
                    group.append(user['person_id'])
                break
            group.append(users[choice_person - 1]['person_id'])

        already_have = False
        for gr in groups:
            if Counter(gr) == Counter(group):
                group_id = receipt_positions[groups.index(gr)]['group_id']
                already_have = True
                break
        if already_have is False:
            group_id = db.add_paid_person_group()

        receipt_positions.append(
            {
                'gathering_id': gathering_id,
                'description': description,
                'payed_person_id': payed_person_id,
                'group_id': group_id,
                'amount': amount,
                'group': group
            }
        )
        continue_input = input("Хотите добавить еще одну позицию? (Да/Нет): ").strip().lower()
        if continue_input != 'да':
            break

    return receipt_positions


def create_gathering(company_id):
    print("\n--- Создаем мероприятие ---")
    ind = 0
    date = datetime.date.today().isoformat()
    # Собираем данные, а потом только записываем позиции в бд

    # inline ввод Да/Нет в боте
    today = input("Мероприятие было сегодня?(Да/Нет): ").strip().lower()
    if today == "нет":
        while True:
            date = input("Введите дату в формате YYYY-MM-DD: ")
            if re.match(date_regex, date):
                break
            else:
                print("Sorry not sorry\n")

    locate = input("Введите название места: ")
    gathering_id = db.add_gathering(date, locate, company_id)
    receipt_positions = adding_receipt_positions(company_id, gathering_id)

    # TODO добавление позиций или атомарное мероприятие и позиции в методе
    db.start_transaction()
    for position in receipt_positions:
        for person in position['group']:
            db.add_person_to_group(position['group_id'], person)
        db.add_receipt_position(
            position['gathering_id'],
            position['payed_person_id'],
            position['group_id'],
            position['amount'],
            position['description']
        )
    db.end_transaction()


if __name__ == "__main__":
    main_menu()
