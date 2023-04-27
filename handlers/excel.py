from aiogram import types
import pandas as pd
import openpyxl
from bot import bot

filename = 'upload.xlsx'


async def handle_document(message: types.Message):
    file_info = await bot.get_file(message.document.file_id)
    downloaded_file = await bot.download_file(file_info.file_path)
    with open(filename, "wb") as f:
        f.write(downloaded_file.read())
    f.close()
    statistic = await load_excel_to_db()
    await bot.send_message(
        message.chat.id,
        f"Файл обработан:\nСтрок в файле: {statistic.from_file_count}"
        f"\nКорректных строк: {statistic.positions_count}"
        f"\nДобавлено в базу (новых): {statistic.inserted_count}",
    )

async def load_excel_to_db():
    df = pd.read_excel(filename, usecols=[0])
    file_data = df.iloc[:, 0].values.tolist()
    positions = []
    for element in file_data:
        if str(element).isdigit():
            positions.append(int(element))

    source_db = SourceScraper(table_name="oreht_positions")
    for position in positions:
        source_db.insert_into_source_table(position, now)
    inserted_count = source_db.insert_count_by_date(now)
    positions_count = len(positions)
    from_file_count = len(file_data)
    source_db.close_connection()
    return ExcelImportStats(
        inserted_count=inserted_count,
        positions_count=positions_count,
        from_file_count=from_file_count,
    )



