import dataclasses
import os

import psycopg2


class Database:
    def __init__(self):
        self.conn = psycopg2.connect(database=os.getenv('DB_NAME'), user=os.getenv('DB_USER'),
                                password=os.getenv('DB_PASSWORD'),
                                host=os.getenv('DB_HOST'), port=os.getenv('DB_PORT'))
        self.cur = self.conn.cursor()

    def get_card_to_check(self, table_name: str):
        self.cur.execute("SELECT * FROM %s WHERE stage = %s LIMIT 1", (table_name, 'Target parsed',))
        row = self.cur.fetchone()
        if row:
            return row[0]
        return None


    def save_card_result(self):
        pass
