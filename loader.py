from aiogram import Bot, Dispatcher
import os

bot = Bot(os.getenv('BOT_TOKEN'))
dp = Dispatcher(bot)