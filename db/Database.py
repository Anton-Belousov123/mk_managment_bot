import random

import pandas as pd

from sc import secret
import psycopg2
import dataclasses


@dataclasses.dataclass
class DBObj:
    s_article: str
    s_name: str
    s_url: str
    s_photo: str
    s_price: float
    t_name: str
    t_url: str
    t_photo: str
    t_price: float
    t_type: str
    stage: str
    t_article: int


@dataclasses.dataclass
class ExcelImportStats:
    inserted_count: int
    positions_count: int
    from_file_count: int


class Database:
    def __init__(self):
        pass

    def get_code(self, table_name):
        self.conn = psycopg2.connect(
            host=secret.DATABASE_HOST,
            database=secret.DATABASE_NAME,
            user=secret.DATABASE_LOGIN,
            password=secret.DATABASE_PASSWORD,
        )
        self.cur = self.conn.cursor()
        self.cur.execute(f"SELECT * FROM {table_name} WHERE stage=%s", ("Target parsed",))
        records = self.cur.fetchall()
        self.conn.close()
        if not records:
            return None
        record = random.choice(records)
        return DBObj(
            record[0], record[1], record[2], record[3], record[4], record[5], record[6], record[7], record[8],
            record[9], record[10], record[11])

    def set_success(self, data, table_name):
        self.conn = psycopg2.connect(
            host=secret.DATABASE_HOST,
            database=secret.DATABASE_NAME,
            user=secret.DATABASE_LOGIN,
            password=secret.DATABASE_PASSWORD,
        )
        self.cur = self.conn.cursor()
        t_article = data.data.split('_')[1]
        s_article = data.data.split('_')[2]
        self.cur.execute(f"UPDATE {table_name} SET stage=%s WHERE s_article=%s AND t_article=%s",
                         ('Suggested', s_article, t_article,))
        self.conn.commit()
        self.cur.execute(f"DELETE FROM {table_name} WHERE s_article=%s AND stage!=%s;",
                         (s_article, 'Suggested',))
        self.conn.commit()
        self.conn.close()

    def set_decline(self, data, table_name):
        self.conn = psycopg2.connect(
            host=secret.DATABASE_HOST,
            database=secret.DATABASE_NAME,
            user=secret.DATABASE_LOGIN,
            password=secret.DATABASE_PASSWORD,
        )
        self.cur = self.conn.cursor()
        t_article = data.data.split('_')[1]
        s_article = data.data.split('_')[2]
        self.cur.execute(f"DELETE FROM {table_name} WHERE s_article=%s AND t_article=%s",
                         (s_article, t_article,))
        self.conn.commit()
        self.conn.close()

    def load_excel_to_db(self):
        self.conn = psycopg2.connect(
            host=secret.DATABASE_HOST,
            database=secret.DATABASE_NAME,
            user=secret.DATABASE_LOGIN,
            password=secret.DATABASE_PASSWORD,
        )
        self.cur = self.conn.cursor()
        filename = 'upload.xlsx'
        df = pd.read_excel(filename, usecols=[0])
        file_data = df.iloc[:, 0].values.tolist()
        positions = []
        for element in file_data:
            if str(element).isdigit():
                positions.append(int(element))
        inserted_count = 0
        for position in positions:
            try:
                inserted_count += 1
                self.cur.execute(f"INSERT INTO {'kamran'} (s_article, stage) "
                                 f"SELECT %s, %s WHERE NOT EXISTS "
                                 f"(SELECT s_article FROM {'kamran'} WHERE s_article = %s)",
                                 (str(position), "Created", str(position)))
                self.conn.commit()
            except Exception as e:
                print(e)
        positions_count = len(positions)
        from_file_count = len(file_data)
        self.conn.close()
        return ExcelImportStats(
            inserted_count=inserted_count,
            positions_count=positions_count,
            from_file_count=from_file_count,
        )
