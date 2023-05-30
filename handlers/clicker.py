import datetime
import json
import os

from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove, ReplyKeyboardMarkup, \
    KeyboardButton, InputMediaPhoto
from PIL import Image, ImageFont, ImageDraw
from bot import dp, bot, olegs_workers, database
import requests


olegs_persons = [1398715343, 791143287, 1142295810, 766551887, 919524762]
stats = {}
date = datetime.datetime.now().day

@dp.message_handler(commands=['stats'])
async def statistic(message: types.Message):
    answer = ''
    for k, v in stats.items():
        answer += f'{k} - {v[0]} / {v[1]} / {v[2]}\n'
    await message.answer(answer)

def download_image(link: str, index, title):
    filename = f"{index}.jpg"
    img_data = requests.get(link).content
    with open(filename, "wb") as handler:
        handler.write(img_data)
    handler.close()
    return filename


async def delete_prev_message(message: types.Message):
    for i in range(5):
        try:
            await bot.delete_message(message.chat.id, message.message_id - i)
        except:
            pass


async def send_item(message: types.Message):
    await delete_prev_message(message)
    table_name = 'kamran'
    if message.chat.id in olegs_persons:
        table_name = 'oleg'
    card = database.get_code(table_name)
    print(card)
    if not card:
        await bot.send_message(chat_id=message.chat.id, text='На данный момент доступных к обработке карточек нет!',
                               reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton(text="Попробовать еще раз")))

    else:
        print(card.t_photo)
        t_photos = json.loads(card.t_photo.replace("'", '"'))
        print(t_photos)
        arr = []
        try:
            arr.append(InputMediaPhoto(open(download_image(card.s_photo, -1, 'Source'), "rb"), caption="Source"))
        except:
            await message.answer(text="Oreht: " + card.s_photo)
        for i in range(len(t_photos)):
            arr.append(InputMediaPhoto(open(download_image(t_photos[i], i, 'MarketPlace'), "rb"), caption=f"Marketplace{i}"))
            if len(arr) == 4:
                break
        try:
            await bot.send_media_group(message.chat.id, media=arr)
        except:
            pass
        text = f"Источник:\n№ {card.s_article}\nИмя: {card.s_name}\nЦена: {card.s_price}\n<a href='{card.s_url}'>Посмотреть товар</a>"
        text += f"\n\nМаркетплейс:\n№ {card.t_article}\nИмя: {card.t_name}\nЦена: {card.t_price}\n<a href='{card.t_url}'>Посмотреть товар</a>"
        reply_markup = InlineKeyboardMarkup()
        reply_markup.add(
            InlineKeyboardButton(text='✅', callback_data=f'approve_{card.t_article}_{card.s_article}'),
            InlineKeyboardButton(text='±', callback_data=f'plus-minus_{card.t_article}_{card.s_article}'),
            InlineKeyboardButton(text='❌', callback_data=f'reject_{card.t_article}_{card.s_article}')
        )
        await bot.send_message(chat_id=message.chat.id, text=text, reply_markup=reply_markup, parse_mode="HTML", disable_web_page_preview=True)


@dp.callback_query_handler(lambda data: 'approve' in data.data)
async def approve_button_handler(data):
    global stats
    global date
    if str(date) != str(datetime.datetime.now().day):
        date = datetime.datetime.now().day
        stats = {}
    name = str(data.message.from_user.first_name) + ' ' + str(data.message.from_user.last_name) + ' ' + str(
        data.message.from_user.username)
    try:
        stats[name][0] += 1
    except:
        stats[name] = [1, 0, 0]
    table_name = 'kamran'
    if data.message.chat.id in olegs_persons:
        table_name = 'oleg'
    database.set_success(data, table_name)
    await data.answer("Согласовано!")
    await send_item(data.message)




@dp.callback_query_handler(lambda data: 'plus-minus' in data.data)
async def plus_minus_handler(data):
    global stats

    global date
    if str(date) != str(datetime.datetime.now().day):
        date = datetime.datetime.now().day
        stats = {}
    name = str(data.message.from_user.first_name) + ' ' + str(data.message.from_user.last_name) + ' ' + str(
        data.message.from_user.username)
    try:
        stats[name][1] += 1
    except:
        stats[name] = [0, 1, 0]
    table_name = 'kamran'
    if data.message.chat.id in olegs_persons:
        table_name = 'oleg'
    database.set_plus_minus(data, table_name)
    await data.answer("Принято!")
    await send_item(data.message)


@dp.callback_query_handler(lambda data: 'reject' in data.data)
async def reject_button_handler(data):
    global stats

    global date
    if str(date) != str(datetime.datetime.now().day):
        date = datetime.datetime.now().day
        stats = {}
    name = str(data.message.from_user.first_name) + ' ' + str(data.message.from_user.last_name) + ' ' + str(data.message.from_user.username)
    try:
        stats[name][2] += 1
    except:
        stats[name] = [0, 0, 1]
    table_name = 'kamran'
    if data.message.chat.id in olegs_persons:
        table_name = 'oleg'
    database.set_decline(data, table_name)
    await data.answer("Удалено!")
    await send_item(data.message)


@dp.message_handler(lambda m: m.text == 'Поиск товара' or m.text == 'Попробовать еще раз')
async def item_search_handler(message: types.Message):
    await message.answer(text='Поиск...', reply_markup=ReplyKeyboardRemove())
    await send_item(message)
