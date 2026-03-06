import logging
import asyncio
import sys
import os
# pip install aiogram

sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'ui_python', 'modules'))
from backend_connector import BackendConnector

API_TOKEN = 'YOUR_TELEGRAM_BOT_TOKEN'

# from aiogram import Bot, Dispatcher, types
# from aiogram.filters import Command

print("Telegram Bot module created. Install aiogram to run.")
print("Logic: Bot receives message -> Calls BackendConnector -> Calls C++ Core -> Sends Reply")