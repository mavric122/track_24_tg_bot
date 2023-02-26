import logging
import asyncio
from aiogram import Bot, Dispatcher, types
import aiohttp
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from bs4 import BeautifulSoup
import datetime

from Secret import TOKEN

# устанавливаем уровень логов
logging.basicConfig(level=logging.INFO)

# инициализируем бота
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)


# настраиваем соединение с базой данных
async def on_startup(dp):
    logging.warning(
        'Starting connection. ')
    await bot.send_message(chat_id='337878153', text='Бот запущен')


async def on_shutdown(dp):
    logging.warning('Shutting down..')
    await bot.send_message(chat_id='337878153', text='Бот остановлен')
    await bot.close()
    await dp.storage.close()
    await dp.storage.wait_closed()


async def get_exchange_track():
    async with aiohttp.ClientSession() as session:
        async with session.get('https://track24.ru/?code=QR20709448') as response:
            if response.status == 200:
                div = await response.text()
                soup = BeautifulSoup(div, 'html.parser')
                description = soup.find('meta', {'property': 'og:description'})['content']
                # print("Поиск реально выполнился.")
                return description
            else:
                print("Not 200")


# регистрируем обработчик команды старта
@dp.message_handler(commands=['start'])
async def start_handler(message: types.Message):
    button1 = InlineKeyboardButton(text='Кнопка 1', callback_data='button1')
    button2 = InlineKeyboardButton(text='Кнопка 2', callback_data='button2')
    # Создание разметки с кнопками
    markup = InlineKeyboardMarkup().add(button1, button2)
    # Отправка сообщения с разметкой
    await bot.send_message(chat_id=message.chat.id, text='Выберите действие:', reply_markup=markup)
    async with aiohttp.ClientSession() as session:
        rate = await get_exchange_track()

        old_location = 0
        flag = True
        await message.answer(f"Привет, {message.from_user.full_name}!\n Новое местоположение посылки: \n {rate}")
        while True:
            if rate != old_location:
                if flag:
                    print("Начали!")
                    old_location = rate
                    time_now = datetime.datetime.now()
                    print(f"Жду час, начало в: " + str(time_now))
                    await asyncio.sleep(3600)
                    flag = True
                    print("Подождал час")
                else:
                    print("-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=")
                    print("Новое местоположение")
                    print("-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=")
                    time_now = datetime.datetime.now()
                    print(f"Жду час, начало в" + str(time_now))
                    await asyncio.sleep(3600)
                    print("Подождал час")
            else:
                print("Старое местоположение")
                time_now = datetime.datetime.now()
                print(f"Жду час, начало в" + str(time_now))
                await asyncio.sleep(3600)
                print("Подождал час")
                continue


@dp.message_handler(commands=['Где?'])
async def where_track(message: types.Message):
    async with aiohttp.ClientSession() as session:
        rate = await get_exchange_track()

        old_location = 0
        await message.answer(f"Посылка сейчас: \n {rate}")
        print("Запрос местоположения!")


# запускаем лонг поллинг
if __name__ == '__main__':
    from aiogram import executor

    executor.start_polling(dp, on_startup=on_startup, on_shutdown=on_shutdown)
