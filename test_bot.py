import logging
import sys
import locale
import asyncio
from aiogram import Bot, Dispatcher, types
import aiohttp
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, message
from aiogram.utils import executor
from bs4 import BeautifulSoup
import datetime

from Secret import TOKEN

# Установить кодировку вывода в консоль
sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf8', buffering=1)

# Установить локаль для поддержки кириллицы в Windows
if sys.platform == 'win32':
    locale.setlocale(locale.LC_ALL, 'Russian_Russia.1251')

# Инициализация бота и диспетчера
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)


async def get_exchange_track():
    async with aiohttp.ClientSession() as session:
        async with session.get('https://track24.ru/?code=QR20709448') as response:
            if response.status == 200:
                div = await response.text()
                # print(div)
                soup = BeautifulSoup(div, 'html.parser')
                print(soup)
                description = soup.find('meta', {'property': 'og:description'})['content']
                return description
            else:
                print("Not 200")


# Функция для обработки нажатия на кнопку "Where"
async def where_tracking(query: types.CallbackQuery):
    async with aiohttp.ClientSession() as session:
        rate = await get_exchange_track()

        old_location = 0
        await bot.send_message(chat_id=query.message.chat.id, text=f"Посылка сейчас: \n {rate}")
        print("Запрос местоположения!")


def time_now():
    return str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))


# Функция для обработки нажатия на кнопку "Start"
async def start_tracking(query: types.CallbackQuery):
    await bot.send_message(chat_id=query.from_user.id, text='Вы нажали кнопку "Start"')
    async with aiohttp.ClientSession() as session:
        rate = await get_exchange_track()
        old_location = 0

        flag = True
        await bot.send_message(chat_id=query.message.chat.id, text=f"Привет!\n Новое местоположение посылки: \n {rate}")
        while True:
            if rate != old_location:
                if flag:
                    print("Начали!")
                    old_location = rate
                    print(f"Жду час, начало в: " + time_now())
                    await asyncio.sleep(3600)
                    flag = False
                    print("Подождал час")
                else:
                    print("-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=")
                    print("Новое местоположение")
                    print("-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=")
                    await bot.send_message(chat_id=query.message.chat.id,
                                           text=f"Новое местоположение посылки:" + str(rate))
                    print(f"Жду час, начало в" + time_now())
                    await asyncio.sleep(3600)
                    print("Подождал час")
            else:
                print("Старое местоположение")
                print(f"Жду час, начало в " + time_now())
                await asyncio.sleep(3600)
                print("Подождал час")
                continue


# Обработчик команды /start
@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    # Создание кнопок
    button_where = InlineKeyboardButton(text='Where', callback_data='where')
    button_start = InlineKeyboardButton(text='Start', callback_data='start')
    # Создание разметки с кнопками
    markup = InlineKeyboardMarkup().add(button_where, button_start)
    # Отправка сообщения с разметкой
    await bot.send_message(chat_id=message.chat.id, text='Выберите действие:', reply_markup=markup)


# Обработчик нажатий на кнопки
@dp.callback_query_handler(lambda c: c.data == 'where')
async def process_where_callback(callback_query: types.CallbackQuery):
    await where_tracking(callback_query)


@dp.callback_query_handler(lambda c: c.data == 'start')
async def process_start_callback(callback_query: types.CallbackQuery):
    await start_tracking(callback_query)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)

