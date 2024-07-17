import datetime

from aiogram import types, Router
from aiogram.types import Message, LabeledPrice, KeyboardButton, ReplyKeyboardMarkup, FSInputFile
from aiogram.filters import Command
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import config
from main import bot
import pandas as pd

# создаю словарь для отслеживания состояний пользователя
user_state = {}

# обращение к гугл табличке из облака
# scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
# creds = ServiceAccountCredentials.from_json_keyfile_name('tgbotproject-429411-291b168c5f55.json', scope)
# client = gspread.authorize(creds)

router = Router()

# кнопки для взаимодействия с ботом
button1 = KeyboardButton(text="Ленина 1 (Яндекс карты)")
button2 = KeyboardButton(text="Оплатить 2 рубля")
button3 = KeyboardButton(text="Картинка")

button4 = KeyboardButton(text=f"Значение A2 {config.TABLE_NAME} API")
button5 = KeyboardButton(text="Ввести дату API")

button6 = KeyboardButton(text=f"Значение A2 {config.TABLE_NAME} offline")
button7 = KeyboardButton(text="Ввести дату offline")

# клавиатура бота
keyboard = ReplyKeyboardMarkup(keyboard=[[button1], [button2], [button3], [button4], [button5], [button6], [button7]],
                               resize_keyboard=True)


# обработчик комманды /start
@router.message(Command("start"))
async def start(msg: Message):
    await msg.answer('Выбери действие', reply_markup=keyboard)


# обработчик button1
@router.message(lambda msg: msg.text == "Ленина 1 (Яндекс карты)")
async def map_handler(msg: Message):
    # инициализация кнопки с ссылкой на яндекс карты
    url = "https://yandex.ru/maps/38/volgograd/house/prospekt_imeni_v_i_lenina_1b/YE0YcwZgTEQBQFpifXtxcnlibA==/?indoorLevel=1&ll=44.510517%2C48.703518&z=17.08"

    button = [
        [
            types.InlineKeyboardButton(text="Открыть Яндекс карты", url=url)
        ]
    ]
    kb = types.InlineKeyboardMarkup(inline_keyboard=button)
    await msg.answer("Вот и ссылка на карты", reply_markup=kb)


# обработчик button2
@router.message(lambda msg: msg.text == "Оплатить 2 рубля")
async def pay_handler(msg: Message):
    # создание платежа
    await bot.send_invoice(
        chat_id=msg.chat.id,
        title='Какая то покупка',
        description='Описание',
        payload='invoice',
        provider_token=config.PAY_TOKEN,
        currency='RUB',
        prices=[

            LabeledPrice(
                label='Pay',
                amount=200 * 100
            )

        ]
    )


# обработчик button3 - отправка картинки пользователю
@router.message(lambda msg: msg.text == "Картинка")
async def img_handler(msg: Message):
    image_from_pc = FSInputFile("img1.jpg")
    await msg.answer_photo(
        image_from_pc,
        caption="Картинка - img1.jpg"
    )


# для таблицы из облака(обращение по апи)

# обработчик button4 - взятие значение из таблицы
# @router.message(lambda msg: msg.text == f"Значение A2 {config.TABLE_NAME} API")
# async def table_handler(msg: Message):
#     # открываю таблицу и обращаюсь к ячейке A2 по координатам
#     sheet = client.open(f"{config.TABLE_NAME}").sheet1
#     data = sheet.cell(2, 1).value
#     await msg.answer(f'Значение ячейки А2 {config.TABLE_NAME}: {data}')
#
#
# # обработчик button5 - ввод даты для занесения в таблицу
# @router.message(lambda msg: msg.text == "Ввести дату API")
# async def input_handler(msg: Message):
#     # изменение состояния пользователя
#     user_state[msg.from_user.id] = "awaiting_date"
#     await msg.answer(f'Введите дату в формате %d.%m.%y, она будет помещена в ячейку B2 таблицы')


@router.message(lambda msg: msg.text == f"Значение A2 {config.TABLE_NAME} offline")
async def table_handler(msg: Message):
    sheet = pd.read_csv("гугл_табличка.csv", header=None)
    await msg.answer(f"Значение ячейки А2 гугл_таблички: {sheet.iloc[1, 0]}")


@router.message(lambda msg: msg.text == "Ввести дату offline")
async def input_handler(msg: Message):
    # изменение состояния пользователя
    user_state[msg.from_user.id] = "awaiting_date"
    await msg.answer(f'Введите дату в формате %d.%m.%y, она будет помещена в ячейку B2 таблицы')


# для "оффлайн" таблицы
@router.message()
async def message_handler(msg: Message):
    user_id = msg.from_user.id
    input_date = msg.text
    # проверка состояния пользователя
    if user_id in user_state and user_state[user_id] == "awaiting_date":
        try:
            # проверка даты на корректность и изменения значения в табличке
            date_format = '%d.%m.%Y'
            datetime.datetime.strptime(input_date, date_format)
            sheet = pd.read_csv("гугл_табличка.csv", header=None)
            sheet.iloc[1, 1] = input_date
            sheet.to_csv("гугл_табличка.csv", header=False, index=False)
            print(input_date)
            await msg.answer("Дата корректно введена, обновлено значение ячейки B2")
            user_state.pop(user_id)
        except ValueError:
            await msg.answer("Дата введена неверно")
    else:
        await msg.answer("Неизвестная команда. Пожалуйста, выберите действие из меню.")

# для таблицы из облака

# обработчик входящего сообщения от пользователя
# @router.message()
# async def message_handler(msg: Message):
#     user_id = msg.from_user.id
#     input_date = msg.text
#     # проверка состояния пользователя
#     if user_id in user_state and user_state[user_id] == "awaiting_date":
#         try:
#             # проверка даты на корректность и изменения значения в табличке
#             date_format = '%d.%m.%Y'
#             datetime.datetime.strptime(input_date, date_format)
#             sheet = client.open(f"{config.TABLE_NAME}").sheet1
#             sheet.update_cell(2, 2, input_date)
#             await msg.answer("Дата корректно введена, обновлено значение ячейки B2")
#             user_state.pop(user_id)
#         except ValueError:
#             await msg.answer("Дата введена неверно")
#     else:
#         await msg.answer("Неизвестная команда. Пожалуйста, выберите действие из меню.")
