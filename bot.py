import os
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from db.Database import Database

load_dotenv()

TOKEN = os.getenv('TELEGRAM_TOKEN')
oleg_id = os.getenv('OLEG_ID')
kamran_id = os.getenv('KAMRAN_ID')
olegs_workers = [os.getenv('ANTON_ID')]
users_stats = {}
bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

database = Database()

from handlers import dp
