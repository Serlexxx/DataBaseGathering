from BasicOperationDBSqlite.db import DataBase


class DataBaseGathering(DataBase):
    def __init__(self, ):
        super().__init__(name="DataBaseGathering.db")

    def _initial_db(self):
        self.execute('''
            CREATE TABLE IF NOT EXISTS "Company" (
                "company_id"	INTEGER NOT NULL UNIQUE,
                "name"	        TEXT NOT NULL,
                "company_hash"	TEXT NOT NULL UNIQUE,
                PRIMARY         KEY("company_id" AUTOINCREMENT)
            );
        ''', ())

        self.execute('''
            CREATE TABLE IF NOT EXISTS "Gathering" (
                "gathering_id"	INTEGER NOT NULL UNIQUE,
                "date"	TEXT,
                "location"	TEXT,
                "company_id"	INTEGER NOT NULL,
                FOREIGN KEY("company_id") REFERENCES "Company"("company_id"),
                PRIMARY KEY("gathering_id")
            );
        ''', ())

        self.execute('''
            CREATE TABLE IF NOT EXISTS "Person" (
                "person_id"	INTEGER NOT NULL UNIQUE,
                "person_name"	TEXT,
                "tg_tag"	TEXT,
                PRIMARY KEY("person_id" AUTOINCREMENT)
            );
        ''', ())

        self.execute('''
            CREATE TABLE IF NOT EXISTS "ReceiptPosition" (
                "receipt_position_id"	INTEGER NOT NULL UNIQUE,
                "description"	TEXT,
                "amount"	INTEGER NOT NULL,
                "gathering_id"	INTEGER NOT NULL,
                "payed_person_id"	INTEGER NOT NULL,
                "group_id"	INTEGER NOT NULL,
                FOREIGN KEY("payed_person_id") REFERENCES "Person",
                PRIMARY KEY("receipt_position_id" AUTOINCREMENT)
            );
        ''', ())

        self.execute('''
            CREATE TABLE IF NOT EXISTS "CompanyPerson" (
                "company_id"	INTEGER NOT NULL,
                "person_id"	INTEGER NOT NULL,
                FOREIGN KEY("person_id") REFERENCES "Person"("person_id"),
                FOREIGN KEY("company_id") REFERENCES "Company"("company_id")
            );
        ''', ())

        self.execute('''
            CREATE TABLE IF NOT EXISTS "PersonGroup" (
                "group_id"	INTEGER NOT NULL UNIQUE,
                "paid"	BLOB NOT NULL,
                PRIMARY KEY("group_id" AUTOINCREMENT)
            );
        ''', ())

        self.execute('''
            CREATE TABLE IF NOT EXISTS "PersonGroupPerson" (
                "group_id"	INTEGER NOT NULL,
                "person_id"	INTEGER NOT NULL,
                FOREIGN KEY("person_id") REFERENCES "Person"("person_id"),
                FOREIGN KEY("group_id") REFERENCES "PersonGroup"("group_id")
            );
        ''', ())
