from DataBaseGathering import DataBaseGathering as DBG

from random import randint
from sys import maxsize
import datetime
import re
import pandas as pd

date_regex = re.compile(r'\d{4}-\d{2}-\d{2}')

db = DBG()


def default_start_menu(choice, target_user):
    company_id = None
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


def default_while_not_true_input(string_0, string_1, condition):
    while True:
        get_value = input(f"{string_0} " + (f"({string_1}): " if string_1 else ": "))
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

    choice = int(default_while_not_true_input(f"{ind_menu + 1}. Создать компанию\n"
                                              f"{ind_menu + 2}. Присоедениться к компании\n"
                                              f"Выберите действие",
                                              "0 - выход",
                                              lambda value: int(value) >= 0))
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

    choice = int(default_while_not_true_input("Выберите действие",
                                              "0 - в главное меню",
                                              lambda value: int(value) >= 0))

    if choice == 1:
        add_user_in_company(company_id, None)
    elif choice == 2:
        get_all_user_in_company(company_id)
    elif choice == 3:
        create_gathering(company_id)
    elif choice == 4:
        # TODO menu_5 вывод списка мероприятий
        edit_gathering(company_id)
    elif choice == 5:
        show_gathreing(company_id)
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
    name = default_while_not_true_input("Введите название компании", None,
                                        lambda value: value is not None and value.strip() != "")
    hex_company = hex(hash((randint(0, maxsize), name)))[2:]
    last_row = db.add_company(name, hex_company)
    print(f"Компания '{name}' добавлена.\nОтправьте hash своим друзьям: '{hex_company}'\n")
    add_user_in_company(last_row, target_user)
    return last_row


def authorization_user():
    print("\n--- Авторизация user ---")
    # user_tag = default_while_not_true_input("Введите tg tag", None,
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
        user_tag = default_while_not_true_input("Введите tg tag", None,
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
    hex_company = default_while_not_true_input("Введите hash компании", None,
                                               lambda value: value is not None and value.strip() != "")
    company = db.find_company(hex_company)
    if company is None:
        print(f"Компания с таким hash '{hex_company}' не существует. Попробуйте снова\n")
        return 0
    else:
        print(f"Присоединяемся к компании: '{company['name']}'\n")
        add_user_in_company(company['company_id'], target_user)
        return company['company_id']


def get_array_selected_person(array, original_array, string):
    ind = 0

    for user in original_array:
        ind += 1
        print(f"{ind}. {user['tg_tag']}")
    while True:
        if len(array) == len(original_array):
            print("Всех отметили")
            break
        choice_person = int(default_while_not_true_input(string,
                                                         "-1 - все; 0 - закончить",
                                                         lambda value: (-1 <= int(value) <= len(original_array))))
        if choice_person == 0:
            if len(array) == 0:
                print("Еще не выбрали никого\n")
                continue
            else:
                break
        elif choice_person == -1:
            array = []
            for user in original_array:
                array.append(user)
            break
        choice_person -= 1
        if choice_person < len(original_array):
            if not original_array[choice_person] in array:
                array.append(original_array[choice_person])
            else:
                print(f"Уже отметили {original_array[choice_person]['tg_tag']}")

    return array


def adding_receipt_positions(who_was):
    global group_id
    print("\n--- Заполняем чеки ---")
    groups = []

    while True:
        data_payment_status = []
        group = []

        description = default_while_not_true_input("Введите название позицию чека", None,
                                                   lambda value: value is not None and value.strip() != "")
        amount = float(default_while_not_true_input("Введите цену позиции чека", None,
                                                    lambda value: float(value)))
        # Собираем кто заказывал эту позицию
        group = get_array_selected_person(group, who_was, "Кто заказывал?")

        choice_payed_person_id = int(default_while_not_true_input("Кто платил за позицию?", ">0",
                                                                  lambda value: 0 < int(value) <= len(who_was))) - 1
        payed_person_id = who_was[choice_payed_person_id]['person_id']

        for person in group:
            data_payment_status.append(
                {
                    # Если платил я же, то ставим статус ОПЛАЧЕНО
                    'is_paid': 1 if person['person_id'] == payed_person_id else 0,
                    'person_id': person['person_id'],
                }
            )
        data_receipt_positions = {
            'description': description,
            'payed_person_id': payed_person_id,
            'amount': amount,
            'data_payment_status': data_payment_status,
        }

        already_have = False
        if groups:
            for gr in groups:
                if gr['group'] == group:
                    print(gr['group'], group)
                    gr['data_receipt_positions'].append(data_receipt_positions)
                    already_have = True
                    break
        if already_have is False:
            groups.append(
                {
                    'group': group,
                    'count_person': len(group),
                    'data_receipt_positions': [data_receipt_positions],
                }
            )

        continue_input = default_while_not_true_input("Хотите добавить еще одну позицию?", "Да/Нет",
                                                      lambda
                                                          value: value is not None and value.strip() != "").strip().lower()
        if continue_input != 'да':
            break

    return groups


def create_gathering(company_id):
    print("\n--- Создаем мероприятие ---")
    who_was = []
    users = db.get_all_user_in_company(company_id)
    date = datetime.date.today().isoformat()
    # Собираем данные, а потом только записываем позиции в бд

    # inline ввод Да/Нет в боте
    today = default_while_not_true_input("Мероприятие было сегодня?", "Да/Нет",
                                         lambda value: value is not None and value.strip() != "").strip().lower()
    if today == "нет":
        date = default_while_not_true_input("Введите дату", "YYYY-MM-DD",
                                            lambda value: re.match(date_regex, value))

    locate = default_while_not_true_input("Введите название места", None,
                                          lambda value: value is not None and value.strip() != "")

    who_was = get_array_selected_person(who_was, users, "Кто был?")
    group_receipt_positions = adding_receipt_positions(who_was)

    # TODO добавление позиций или атомарное мероприятие и позиции в методе
    db.start_transaction()
    gathering_id = db.add_gathering(date, locate, company_id)
    for group_data in group_receipt_positions:
        new_group_id = db.add_person_group(group_data['count_person'])
        for data_receipt in group_data['data_receipt_positions']:
            receipt_position_id = db.add_receipt_position(
                data_receipt['description'],
                data_receipt['amount'],
                gathering_id,
                data_receipt['payed_person_id'],
            )
            for data_person in data_receipt['data_payment_status']:
                payment_status_id = db.add_payment_status(data_person['person_id'], new_group_id,
                                                          data_person['is_paid'])
                db.add_receipt_person_status(receipt_position_id, payment_status_id)
    db.end_transaction()


def edit_gathering(company_id):
    ind = 0
    # TODO переписать под новую структуру БД
    # Выбор мероприятия
    # gatherings = db.get_last_n_gathering(company_id, 5)
    # if not gatherings:
    #     print(f"Не было еще мероприятий\n")
    #     return
    # for gath in gatherings:
    #     ind += 1
    #     print(f"{ind}. {gath['name']} ({gath['date']})")
    # choice_gath = int(default_while_not_true_input("Выберите мероприятие", "0 - назад", lambda value: int(value) >= 0))
    # if choice_gath == 0:
    #     return
    # elif choice_gath > len(gatherings):
    #     print("Invalid imput value")
    #     return
    # receipt_positions = db.get_all_receipt_positions(gatherings[choice_gath - 1]['gathering_id'])
    # ind = 0
    # for receipt in receipt_positions:
    #     ind += 1
    #     # Получаем
    #     # {receipt['gathering_id']}
    #     # {receipt['description']}
    #     # {receipt['amount']}
    #     # {receipt['payed_person_id']}
    #     # {receipt['group_id']}
    #     # {receipt['person_name']}
    #     # {receipt['tg_tag']}
    #     # {receipt['payer_name']}
    #     # {receipt['payer_tg_tag']}
    #     # {receipt['paid']}
    #     # TODO оплачено ли, кто платил, кто заказывал(все люди)
    #     print(f"{ind}. {receipt['description']:<30} - "
    #           f"{receipt['amount']} РУБ "
    #           f"[заказывал - {receipt['person_name']}({receipt['tg_tag']})] "
    #           f"[платил - {receipt['payer_name']}({receipt['payer_tg_tag']})] "
    #           f"({'ОПЛАЧЕНО' if receipt['paid'] != 0 else 'НЕОПЛАЧЕНО'})")
    # choice_receipt = int(default_while_not_true_input(f"{ind + 1}. Добавить позиции\n"
    #                                                   f"Выберите позицию чека",
    #                                                   "0 - назад",
    #                                                   lambda value: int(value) > 0))
    # if choice_receipt == 0:
    #     return
    # elif choice_receipt == ind + 1:
    #     receipt_positions = adding_receipt_positions(gatherings[choice_gath - 1]['gathering_id'])
    #
    #     # TODO добавление позиций или атомарное мероприятие и позиции в методе
    #     db.start_transaction()
    #     for position in receipt_positions:
    #         for person in position['group']:
    #             db.add_person_to_group(position['group_id'], person)
    #         db.add_receipt_position(
    #             position['gathering_id'],
    #             position['payed_person_id'],
    #             position['group_id'],
    #             position['amount'],
    #             position['description']
    #         )
    #     db.end_transaction()
    # else:
    #     # TODO edit receipt_position
    #     pass


def choise_gathering_from_n(company_id):
    ind = 0
    gatherings = db.get_last_n_gathering(company_id, 5)
    if not gatherings:
        print(f"Не было еще мероприятий\n")
        return 0
    for gath in gatherings:
        ind += 1
        print(f"{ind}. {gath['name']} ({gath['date']})")
    choice_gath = int(default_while_not_true_input("Выберите мероприятие", "0 - назад",
                                                   lambda value: 0 <= int(value) < len(gatherings)))
    if choice_gath == 0:
        return 0

    return gatherings[choice_gath - 1]['gathering_id']


def show_full_info(gathering_id):
    receipt_positions = db.get_all_receipt_position(gathering_id)

    result = []
    for pos in receipt_positions:
        payment_statuses = db.get_payment_status(pos['receipt_position_id'])

        row = {
            "Позиция": pos['description'],
            "Цена": pos['amount'],
            "Кто платил": pos['payed_tg_tag'],
        }

        for status in payment_statuses:
            share = pos['amount'] / db.get_count_group(status['group_id'])['count_person']
            user_col = status['tg_tag']
            payment_status = "V" if status['is_paid'] else "X"
            row[user_col] = f"{share:.2f} руб, {payment_status}"

        result.append(row)

    print(pd.DataFrame(result))


def show_gathreing(company_id):
    print("\n--- Показываем мероприятия ---")
    gathering_id = choise_gathering_from_n(company_id)
    if gathering_id == 0:
        return
    show_full_info(gathering_id)



if __name__ == "__main__":
    main_menu()
