from aiogram import types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from bot import dp, users_stats


@dp.message_handler(commands=['start', 'help'])
async def hello_handler(message: types.Message):
    text = "Привет!\nНажимай на кнопку `Поиск товара` и выполняй задания!"
    reply_markup = ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton("Поиск товара"))
    await message.answer(text=text, reply_markup=reply_markup)


@dp.message_handler(commands=['/stats'])
async def stats_handler(message: types.Message):
    u_s = ''
    for v, k in users_stats.items():
        u_s += f'{v}: {k}\n'
    await message.answer(u_s)
