from BasicOperationDBSqlite.db import DataBase



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

    def add_person(self, tg_tag):
        self.execute('''
            INSERT INTO "Person" ("tg_tag") VALUES (?);
        ''', (tg_tag,))
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

    def add_person_and_link_to_company(self, company_id, tg_tag):
        self.start_transaction()
        person_id = self.add_person(tg_tag)
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

    def add_receipt_position(self, description, amount, gathering_id, payed_person_id):
        self.execute('''
            INSERT INTO "ReceiptPosition" ("description", "amount", "gathering_id", "payed_person_id")
            VALUES (?, ?, ?, ?);
        ''', (description, amount, gathering_id, payed_person_id))
        return self.get_last_rowid()

    def get_all_receipt_position(self, gathering_id):
        return self.execute_with_all_result('''
            SELECT 
                rp.receipt_position_id AS receipt_position_id,
                rp.description AS description,
                rp.amount AS amount,
                p.tg_tag AS payed_tg_tag
            FROM ReceiptPosition rp
            JOIN Person p ON rp.payed_person_id = p.person_id
            WHERE  rp.gathering_id = (?);
        ''', (gathering_id,))

    def add_person_group(self, count_person):
        self.execute('''
            INSERT INTO "PersonGroup" ("count_person")
            VALUES (?);
        ''', (count_person,))
        return self.get_last_rowid()

    def get_count_group(self, group_id):
        return self.execute_with_one_result('''
            SELECT count_person FROM PersonGroup WHERE group_id = (?);
        ''', (group_id,))

    def add_payment_status(self, person_id, group_id, is_paid=0):
        self.execute('''
            INSERT INTO "PaymentStatus" ("is_paid", "person_id", "group_id")
            VALUES (?, ?, ?);
        ''', (is_paid, person_id, group_id,))
        return self.get_last_rowid()

    def get_payment_status(self, receipt_position_id):
        return self.execute_with_all_result('''
            SELECT 
                rps.receipt_position_id,
                ps.group_id,
                ps.is_paid,
                per.tg_tag
            FROM ReceiptPersonStatus rps
            JOIN PaymentStatus ps ON rps.payment_status_id = ps.payment_status_id
            JOIN Person per ON ps.person_id = per.person_id
            WHERE rps.receipt_position_id = (?);
        ''', (receipt_position_id,))

    def add_receipt_person_status(self, receipt_position_id, payment_status_id):
        self.execute('''
            INSERT INTO "ReceiptPersonStatus" ("receipt_position_id", "payment_status_id")
            VALUES (?, ?);
        ''', (receipt_position_id, payment_status_id,))

    def _initial_db(self):
        self.execute('''
            CREATE TABLE IF NOT EXISTS "Company" (
                "company_id"    INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
                "name"          TEXT NOT NULL,
                "company_hash"  TEXT NOT NULL UNIQUE
            );
        ''', ())

        self.execute('''
            CREATE TABLE IF NOT EXISTS "Gathering" (
                "gathering_id"  INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
                "date"          TEXT NOT NULL,
                "name"          TEXT NOT NULL,
                "company_id"    INTEGER NOT NULL,
                FOREIGN KEY("company_id") REFERENCES "Company"("company_id") ON DELETE CASCADE
            );
        ''', ())

        self.execute('''
            CREATE TABLE IF NOT EXISTS "Person" (
                "person_id"     INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
                "tg_tag"        TEXT NOT NULL
            );
        ''', ())

        # Вспомогательная таблица
        self.execute('''
            CREATE TABLE IF NOT EXISTS "CompanyPerson" (
                "company_id"    INTEGER NOT NULL,
                "person_id"     INTEGER NOT NULL,
                PRIMARY KEY("person_id", "company_id"),
                FOREIGN KEY("person_id")    REFERENCES "Person"("person_id") ON DELETE CASCADE,
                FOREIGN KEY("company_id")   REFERENCES "Company"("company_id") ON DELETE CASCADE
            );
        ''', ())

        self.execute('''
            CREATE TABLE IF NOT EXISTS "PersonGroup" (
                "group_id"          INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
                "count_person"      INTEGER NOT NULL
            );
        ''', ())

        self.execute('''
            CREATE TABLE IF NOT EXISTS "PaymentStatus" (
                "payment_status_id" INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
                "is_paid"           INTEGER NOT NULL DEFAULT 0,
                "person_id"         INTEGER NOT NULL,
                "group_id"          INTEGER NOT NULL,
                FOREIGN KEY("person_id")    REFERENCES "Person"("person_id") ON DELETE CASCADE,
                FOREIGN KEY("group_id")     REFERENCES "PersonGroup"("group_id") ON DELETE CASCADE
            );
        ''', ())

        self.execute('''
            CREATE TABLE IF NOT EXISTS "ReceiptPosition" (
                "receipt_position_id" INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
                "description"         TEXT,
                "amount"              REAL NOT NULL,
                "gathering_id"        INTEGER NOT NULL,
                "payed_person_id"     INTEGER NOT NULL,
                FOREIGN KEY("gathering_id")     REFERENCES "Gathering"("gathering_id") ON DELETE CASCADE,
                FOREIGN KEY("payed_person_id")  REFERENCES "Person"("person_id") ON DELETE CASCADE
            );
        ''', ())

        self.execute('''
            CREATE TABLE IF NOT EXISTS "ReceiptPersonStatus" (
                "receipt_position_id" INTEGER NOT NULL,
                "payment_status_id"   INTEGER NOT NULL,
                PRIMARY KEY("receipt_position_id", "payment_status_id"),
                FOREIGN KEY("receipt_position_id")  REFERENCES "ReceiptPosition"("receipt_position_id") ON DELETE CASCADE,
                FOREIGN KEY("payment_status_id")    REFERENCES "PaymentStatus"("payment_status_id") ON DELETE CASCADE
            );
        ''', ())


