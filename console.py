from DataBaseGathering import DataBaseGathering as DBG
from random import randint
from sys import maxsize

db = DBG()

def main_menu():
    company_id = 0
    while True:
        print("\nГлавное меню:")
        if company_id == 0:
            print("1. Создать компанию")
            print("2. Присоедениться к компании")
            print("3. Выход")

            choice = input("Выберите действие (введите номер): ")

            if choice == "1":
                company_id = create_company()
            elif choice == "2":
                company_id = join_company()
            elif choice == "3":
                print("Выход из программы.")
                break
            else:
                print("Неверный выбор. Попробуйте снова.")
        else:
            return

def create_company():
    print("\n--- Добавление компании ---")
    name = input("Введите название компании: ")
    hex_company = hex(hash((randint(0, maxsize), name)))[2:]
    last_row = db.add_company(name, hex_company)
    print(f"Компания '{name}' добавлена.\nОтправьте hash своим друзьям: '{hex_company}'\n")
    return last_row

def join_company():
    print("\n--- Поиск компании ---")
    hex_company = input("Введите hash компании: ")
    company = db.find_company(hex_company)
    print(f"Компания '{company}'\n")


if __name__ == "__main__":
    main_menu()
