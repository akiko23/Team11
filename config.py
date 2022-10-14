from aiogram import Dispatcher, Bot
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from db import Database

bot = Bot("5601650070:AAGwtGUgpgAA2AODyxhC6aqFjxepihWRGHA")
dp = Dispatcher(bot, storage=MemoryStorage())

db = Database('database.db')
