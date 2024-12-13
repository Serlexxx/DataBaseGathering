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


def default_input_choice(string_0, string_1):
    ret = None
    while ret is None:
        try:
            ret = int(input(f"{string_0} ({string_1}): "))
        except:
            print("Invalid input value")
    return ret


def default_while_not_true_input(string, condition):
    while True:
        get_value = input(f"{string}: ")
        try:
            if condition(get_value):
                break
            else:
                print("Sorry not sorry\n")
        except:
            print("Sorry not sorry\n")
    return get_value



# Самое главное меню
def menu_1(target_user):
    ind_menu = 0
    companies = is_user_in_any_company(target_user)
    if not companies is None:
        for company in companies:
            ind_menu += 1
            print(f"{ind_menu}. Компания '{company['name']}'")

    choice = default_input_choice(f"{ind_menu + 1}. Создать компанию\n"
                                  f"{ind_menu + 2}. Присоедениться к компании\n"
                                  f"Выберите действие",
                                  "0 - выход")

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

    choice = default_input_choice("Выберите действие", "0 - в главное меню")

    if choice == 1:
        add_user_in_company(company_id, None)
    elif choice == 2:
        get_all_user_in_company(company_id)
    elif choice == 3:
        # TODO menu_3 создания
        create_gathering(company_id)
    elif choice == 4:
        edit_gathering(company_id)
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
        elif company_id == 0:
            company_id = None
        else:
            company_id = menu_2(company_id)


def create_company(target_user):
    print("\n--- Добавление компании ---")
    name = default_while_not_true_input("Введите название компании", 
                                        lambda value: value is not None and value.strip() != "")
    hex_company = hex(hash((randint(0, maxsize), name)))[2:]
    last_row = db.add_company(name, hex_company)
    print(f"Компания '{name}' добавлена.\nОтправьте hash своим друзьям: '{hex_company}'\n")
    add_user_in_company(last_row, target_user)
    return last_row


def authorization_user():
    print("\n--- Авторизация user ---")
    # user_tag = default_while_not_true_input("Введите tg tag",
    #                                         lambda value: value is not None and value.strip() != "")
    user_tag = "@Serlex"
    print("\n--- Поиск user в бд ---")
    user = db.find_person(user_tag)
    return {'person_id': None, 'tg_tag': user_tag} if user is None else user


def is_user_in_any_company(user):
    if user['person_id'] is None:
        return None

    return db.find_person_in_any_company(user['person_id'])


def add_user_in_company(company_id, target_user):
    if target_user is None:
        # Добавляем другого человека
        user_tag = default_while_not_true_input("Введите tg tag",
                                                lambda value: value is not None and value.strip() != "")
    else:
        # Добавлем себя в созданную компанию или куда присоеденились
        user_tag = target_user['tg_tag']

    print("\n--- Поиск user в бд ---")
    user = db.find_person(user_tag)
    if user is None:
        print("\n--- Не нашли, регистрируем user в бд ---")
        db.add_person_and_link_to_company(company_id, user_tag)
    else:
        print("\n--- Нашли, присоеденили ---")
        db.add_person_to_company(company_id, user['person_id'])


def get_all_user_in_company(company_id):
    ind = 0
    for user in db.get_all_user_in_company(company_id):
        ind += 1
        print(f"{ind}. ({user['tg_tag']})")
    print("\n")


def join_company(target_user):
    print("\n--- Поиск компании ---")
    hex_company = default_while_not_true_input("Введите hash компании",
                                                lambda value: value is not None and value.strip() != "")
    company = db.find_company(hex_company)
    if company is None:
        print(f"Компания с таким hash '{hex_company}' не существует. Попробуйте снова\n")
        return 0
    else:
        print(f"Присоединяемся к компании: '{company['name']}'\n")
        add_user_in_company(company['company_id'], target_user)
        return company['company_id']


def get_array_selected_person(company_id, array, string):
    ind = 0
    users = db.get_all_user_in_company(company_id)

    for user in users:
        ind += 1
        print(f"{ind}. {user['tg_tag']}")
    while True:
        choice_person = default_input_choice(string, "-1 - все; 0 - закончить")
        if choice_person == 0:
            break
        if choice_person == -1:
            for user in users:
                array.append(user['person_id'])
            break
        if choice_person - 1 <= len(users) and not users[choice_person - 1]['person_id'] in array:
            array.append(users[choice_person - 1]['person_id'])

    return array


def adding_receipt_positions(company_id, gathering_id, who_was):
    global group_id
    print("\n--- Заполняем чеки ---")
    ind = 0
    receipt_positions = []
    groups = [who_was]

    # Получаем всех людей для формирования групп и выбора кто платил за позицию в чеке
    users = db.get_all_user_in_company(company_id)

    while True:
        group = []
        description = default_while_not_true_input("Введите название позицию чека", 
                                                   lambda value: value is not None and value.strip() != "")
        # TODO Добавить проверку, что это float
        amount = default_while_not_true_input("Введите цену позиции чека", 
                                                   lambda value: float(value))

        # Собираем кто заказывал эту позицию
        group = get_array_selected_person(company_id, group, "Кто заказывал?")

        # TODO Добавить проверку, что это int > 0
        choice_payed_person_id = default_input_choice("Кто платил за позицию: ", ">0") - 1
        payed_person_id = users[choice_payed_person_id]['person_id']

        already_have = False
        for gr in groups:
            if Counter(gr) == Counter(group):
                if receipt_positions:
                    # TODO получать id групп из бд для этого мероприятия
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
        continue_input = default_while_not_true_input("Хотите добавить еще одну позицию? (Да/Нет)",
                                                      lambda value: value is not None and value.strip() != "").strip().lower()
        if continue_input != 'да':
            break

    return receipt_positions


def create_gathering(company_id):
    print("\n--- Создаем мероприятие ---")
    who_was = []
    date = datetime.date.today().isoformat()
    # Собираем данные, а потом только записываем позиции в бд

    # inline ввод Да/Нет в боте
    today = default_while_not_true_input("Мероприятие было сегодня?(Да/Нет)",
                                         lambda value: value is not None and value.strip() != "").strip().lower()
    if today == "нет":
        date = default_while_not_true_input("Введите дату в формате YYYY-MM-DD",
                                            lambda value: re.match(date_regex, value))

    locate = default_while_not_true_input("Введите название места",
                                          lambda value: value is not None and value.strip() != "")
    gathering_id = db.add_gathering(date, locate, company_id)
    
    who_was = get_array_selected_person(company_id, who_was, "Кто был?")
    receipt_positions = adding_receipt_positions(company_id, gathering_id, who_was)

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


def edit_gathering(company_id):
    ind = 0
    
    # Выбор мероприятия
    gatherings = db.get_last_n_gathering(company_id, 5)
    for gath in gatherings:
        ind += 1
        print(f"{ind}. {gath['name']} ({gath['date']})")
    choice_gath = default_input_choice("Выберите мероприятие", "0 - назад")
    if choice_gath == 0:
        return
    elif choice_gath > len(gatherings):
        print("Invalid imput value")
        return
    receipt_positions = db.get_all_receipt_positions(gatherings[choice_gath - 1]['gathering_id'])
    ind = 0
    for receipt in receipt_positions:
        ind += 1
        # Получаем
        # {receipt['gathering_id']}
        # {receipt['description']}
        # {receipt['amount']}
        # {receipt['payed_person_id']}
        # {receipt['group_id']}
        # {receipt['person_name']}
        # {receipt['tg_tag']}
        # {receipt['payer_name']}
        # {receipt['payer_tg_tag']}
        # {receipt['paid']}
        # TODO оплачено ли, кто платил, кто заказывал(все люди)
        print(f"{ind}. {receipt['description']:<30} - "
              f"{receipt['amount']} РУБ "
              f"[заказывал - {receipt['person_name']}({receipt['tg_tag']})] "
              f"[платил - {receipt['payer_name']}({receipt['payer_tg_tag']})] "
              f"({'ОПЛАЧЕНО' if receipt['paid'] != 0 else 'НЕОПЛАЧЕНО'})")
    choice_receipt = default_input_choice(f"{ind + 1}. Добавить позиции\n"
                                          f"Выберите позицию чека",
                                          "0 - назад")
    if choice_receipt == 0:
        return
    elif choice_receipt == ind + 1:
        receipt_positions = adding_receipt_positions(company_id, gatherings[choice_gath - 1]['gathering_id'])

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
    else:
        # TODO edit receipt_position
        pass

if __name__ == "__main__":
    main_menu()
