from aiogram import types
import pandas as pd
import openpyxl
from bot import bot, dp, database

filename = 'upload.xlsx'


@dp.message_handler(content_types=[types.ContentType.DOCUMENT])
async def handle_document(message: types.Message):
    file_info = await bot.get_file(message.document.file_id)
    downloaded_file = await bot.download_file(file_info.file_path)
    with open(filename, "wb") as f:
        f.write(downloaded_file.read())
    f.close()
    statistic = database.load_excel_to_db()
    await bot.send_message(
        message.chat.id,
        f"Файл обработан:\nСтрок в файле: {statistic.from_file_count}"
        f"\nКорректных строк: {statistic.positions_count}"
        f"\nДобавлено в базу (новых): {statistic.inserted_count}",
    )
