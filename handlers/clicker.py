import os

from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove, ReplyKeyboardMarkup, \
    KeyboardButton

from bot import dp, bot, olegs_workers, database


def send_item(message: types.Message):
    if message.from_user.id in olegs_workers:
        table_name = os.getenv('OLEG_DB_NAME')
    else:
        table_name = os.getenv('KAMRAN_DB_NAME')
    card = database.get_card_to_check(table_name)
    if not card:
        await bot.send_message(chat_id=message.chat.id, text='На данный момент доступных к обработке карточек нет!',
                               reply_markup=ReplyKeyboardMarkup(KeyboardButton("Попробовать еще раз")))
    else:
        await bot.send_media_group(message.chat.id, media=[source_image, target_image])
        text = 'Новый элемент'
        reply_markup = InlineKeyboardMarkup(
            InlineKeyboardButton(text='✅', callback_data='approve'),
            InlineKeyboardButton(text='❌', callback_data='reject')
        )
        await bot.send_message(chat_id=message.chat.id, text=text, reply_markup=reply_markup, parse_mode="HTML")


@dp.callback_query_handler(lambda data: 'approve' in data.data)
def approve_button_handler(data):
    await data.answer("Согласовано!")


@dp.callback_query_handler(lambda data: 'reject' in data.data)
def reject_button_handler(data):
    await data.answer("Удалено!")


@dp.message_handler(lambda m: m.text == 'Поиск товара' or m.text == 'Попробовать еще раз')
async def item_search_handler(message: types.Message):
    await message.answer(text='Поиск...', reply_markup=ReplyKeyboardRemove())
    await send_item(message)
