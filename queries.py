import sqlite3

class Queries():

    def __init__(self, file: str):
        self.db = file 
        self.connect = sqlite3.connect(self.db)
        self.cursor = self.connect.cursor()


    def get_employee(self) -> list:
        query = """
                SELECT id FROM Employee
                """
        out = self.cursor.execute(query)
        return [i for i, *_ in out]


    def get_shifts(self) -> list:
        query = """
                SELECT * FROM Schedule
                """
        out = self.cursor.execute(query).fetchall()
        return [i for i, *_ in out]
        

    def get_prefs(self) -> dict:
        query = """
                SELECT employee, schedule, ponderation FROM Conditions
                """
        out = self.cursor.execute(query).fetchall()
        return {(e, s): p for e,s,p in out}


    def get_presence(self):
        query = """
                SELECT employee, schedule, presence FROM Conditions
                """ 
        out = self.cursor.execute(query).fetchall()
        return {(e, s): p for e,s,p in out}


if __name__== '__main__':
    queries = Queries("database.db")
    print(queries.get_prefs())