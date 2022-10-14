import sqlite3


class Database:
    def __init__(self, db_file):
        self.connection = sqlite3.Connection(db_file)
        self.cursor = self.connection.cursor()

    def request_to_database(self, request, *args):
        with self.connection:
            return self.cursor.execute(request, *args)

    def user_exists(self, user_id):
        res = self.request_to_database("SELECT `user_id` FROM users WHERE user_id=?", (user_id,)).fetchall()
        return bool(len(res))

    def add_user(self, user_id):
        self.request_to_database(f'INSERT INTO users (user_id) VALUES (?)', (user_id,))

    def set_user_data(self, user_id, column_name, value):
        self.request_to_database(f"UPDATE users SET {column_name}=? WHERE user_id=?", (value, user_id,))

    def get_user_param(self, user_id, param):
        return self.request_to_database(f"SELECT {param} FROM users WHERE user_id=?", (user_id,)).fetchone()[0]

    def reset_data(self, user_id):
        self.request_to_database("DELETE FROM users WHERE user_id=?", (user_id,))

    def get_all_user_params(self, user_id):
        return self.request_to_database("SELECT * FROM users WHERE user_id=?", (user_id,)).fetchall()[0]

    def check_param_on_none(self, user_id):
        c = self.get_all_user_params(user_id)
        return any([c[i] is not None for i in range(len(c))])

