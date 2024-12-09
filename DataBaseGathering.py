from BasicOperationDBSqlite.db import DataBase
from random import randint
from sys import maxsize


class DataBaseGathering(DataBase):
    def __init__(self, ):
        super().__init__(name="Gathering.db")

    def add_company(self, name, company_hash):
        self.execute('''
            INSERT INTO "Company" ("name", "company_hash")
            VALUES (?, ?);
        ''', (name, company_hash))
        return self.get_last_rowid()

    def find_company(self, company_hash):
        return self.execute_with_one_result('''
            SELECT "company_id", "name" FROM "Company" WHERE "company_hash" = ?;
        ''', (company_hash,))

    def add_person(self, person_name, tg_tag):
        self.execute('''
            INSERT INTO "Person" ("person_name", "tg_tag")
            VALUES (?, ?);
        ''', (person_name, tg_tag))
        return self.get_last_rowid()

    def find_person(self, tg_tag):
        return self.execute_with_one_result('''
            SELECT "person_id" FROM "Person" WHERE "tg_tag" = ?;
        ''', (tg_tag,))

    def find_person_in_any_company(self, person_id):
        return self.execute_with_all_result('''
            SELECT Company.company_id, Company.name
            FROM Company
            JOIN CompanyPerson ON Company.company_id = CompanyPerson.company_id
            WHERE CompanyPerson.person_id = ?;
        ''', (person_id,))

    def add_person_to_company(self, company_id, person_id):
        self.execute('''
            INSERT OR REPLACE INTO "CompanyPerson" ("company_id", "person_id")
            VALUES (?, ?);
        ''', (company_id, person_id))

    def get_all_user_in_company(self, company_id):
        return self.execute_with_all_result('''
            SELECT * FROM Person
            JOIN CompanyPerson ON Person.person_id = CompanyPerson.person_id
            WHERE CompanyPerson.company_id = ?;
        ''', (company_id,))

    def add_person_and_link_to_company(self, company_id, person_name, tg_tag):
        self.start_transaction()
        person_id = self.add_person(person_name, tg_tag)
        self.add_person_to_company(company_id, person_id)
        self.end_transaction()
        return person_id

    def add_gathering(self, date, name, company_id):
        self.execute('''
            INSERT INTO "Gathering" ("date", "name", "company_id")
            VALUES (?, ?, ?);
        ''', (date, name, company_id))
        return self.get_last_rowid()
    
    def get_last_n_gathering(self, company_id, cnt):
        return self.execute_with_many_result('''
            SELECT * FROM Gathering
            WHERE company_id = ?;
        ''', (company_id,), cnt)

    def add_receipt_position(self, gathering_id, payed_person_id, group_id, amount, description):
        self.execute('''
            INSERT INTO "ReceiptPosition" ("description", "amount", "gathering_id", "payed_person_id", "group_id")
            VALUES (?, ?, ?, ?, ?);
        ''', (description, amount, gathering_id, payed_person_id, group_id))
        return self.get_last_rowid()

    # TODO
    def get_all_receipt_positions(self, gathering_id):
        return self.execute_with_many_result('''
            SELECT * FROM ReceiptPosition
            WHERE gathering_id = ?;
        ''', (gathering_id,))

    def add_paid_person_group(self, paid=False):
        self.execute('''
            INSERT OR REPLACE INTO "PersonGroup" ("paid")
            VALUES (?);
        ''', (paid,))
        return self.get_last_rowid()

    def add_person_to_group(self, group_id, person_id):
        self.execute('''
            INSERT INTO "PersonGroupPerson" ("group_id", "person_id")
            VALUES (?, ?);
        ''', (group_id, person_id))

    def _initial_db(self):
        self.execute('''
            CREATE TABLE IF NOT EXISTS "Company" (
                "company_id"    INTEGER NOT NULL UNIQUE,
                "name"          TEXT NOT NULL,
                "company_hash"  TEXT NOT NULL UNIQUE,
                PRIMARY KEY("company_id" AUTOINCREMENT)
            );
        ''', ())

        self.execute('''
            CREATE TABLE IF NOT EXISTS "Gathering" (
                "gathering_id"  INTEGER NOT NULL UNIQUE,
                "date"          TEXT NOT NULL,
                "name"          TEXT NOT NULL,
                "company_id"    INTEGER NOT NULL,
                FOREIGN KEY("company_id") REFERENCES "Company"("company_id"),
                PRIMARY KEY("gathering_id")
            );
        ''', ())

        self.execute('''
            CREATE TABLE IF NOT EXISTS "Person" (
                "person_id"     INTEGER NOT NULL UNIQUE,
                "person_name"   TEXT NOT NULL,
                "tg_tag"        TEXT NOT NULL,
                PRIMARY KEY("person_id" AUTOINCREMENT)
            );
        ''', ())

        self.execute('''
            CREATE TABLE IF NOT EXISTS "ReceiptPosition" (
                "receipt_position_id"   INTEGER NOT NULL UNIQUE,
                "description"           TEXT,
                "amount"                REAL NOT NULL,
                "gathering_id"          INTEGER NOT NULL,
                "payed_person_id"       INTEGER NOT NULL,
                "group_id"              INTEGER NOT NULL,
                FOREIGN KEY("payed_person_id") REFERENCES "Person",
                PRIMARY KEY("receipt_position_id" AUTOINCREMENT)
            );
        ''', ())

        self.execute('''
            CREATE TABLE IF NOT EXISTS "CompanyPerson" (
                "company_id"    INTEGER NOT NULL,
                "person_id"     INTEGER NOT NULL,
                PRIMARY KEY("person_id","company_id"),
                FOREIGN KEY("person_id") REFERENCES "Person"("person_id"),
                FOREIGN KEY("company_id") REFERENCES "Company"("company_id")
            );
        ''', ())

        self.execute('''
            CREATE TABLE IF NOT EXISTS "PersonGroup" (
                "group_id"  INTEGER NOT NULL UNIQUE,
                "paid"      BLOB NOT NULL,
                PRIMARY KEY("group_id" AUTOINCREMENT)
            );
        ''', ())

        self.execute('''
            CREATE TABLE IF NOT EXISTS "PersonGroupPerson" (
                "group_id"  INTEGER NOT NULL,
                "person_id" INTEGER NOT NULL,
                PRIMARY KEY("group_id","person_id"),
                FOREIGN KEY("person_id") REFERENCES "Person"("person_id"),
                FOREIGN KEY("group_id") REFERENCES "PersonGroup"("group_id")
            );
        ''', ())
