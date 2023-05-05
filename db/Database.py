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
        self.table_name = 'kamran'
        self.conn = psycopg2.connect(
            host=secret.DATABASE_HOST,
            database=secret.DATABASE_NAME,
            user=secret.DATABASE_LOGIN,
            password=secret.DATABASE_PASSWORD,
        )
        self.cur = self.conn.cursor()

    def get_code(self):
        self.cur.execute(f"SELECT * FROM {self.table_name} WHERE stage=%s", ("Target parsed",))
        record = self.cur.fetchone()
        if not record:
            return None
        return DBObj(
            record[0], record[1], record[2], record[3], record[4], record[5], record[6], record[7], record[8],
            record[9], record[10], record[11])

    def set_success(self, data):
        t_article = data.data.split('_')[1]
        s_article = data.data.split('_')[2]
        self.cur.execute(f"UPDATE {self.table_name} SET stage=%s WHERE s_article=%s AND t_article=%s",
                         ('Suggested', s_article, t_article,))
        self.conn.commit()

    def set_decline(self, data):
        t_article = data.data.split('_')[1]
        s_article = data.data.split('_')[2]
        self.cur.execute(f"DELETE FROM {self.table_name} WHERE s_article=%s AND t_article=%s",
                         (s_article, t_article,))
        self.conn.commit()

    def load_excel_to_db(self):
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
                self.cur.execute(f"INSERT INTO {self.table_name} (s_article) "
                                 f"SELECT %s WHERE NOT EXISTS "
                                 f"(SELECT s_article FROM {self.table_name} WHERE s_article = %s)",
                                 (str(position),str(position)))
                self.conn.commit()
            except Exception as e:
                print(e)
        positions_count = len(positions)
        from_file_count = len(file_data)
        return ExcelImportStats(
            inserted_count=inserted_count,
            positions_count=positions_count,
            from_file_count=from_file_count,
        )