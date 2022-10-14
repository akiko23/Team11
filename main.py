import json
import time

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import ParseMode, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor
from aiogram.utils.exceptions import BadRequest

import markups
from config import dp, bot, db
from get_user_data import process_first, process_second, process_user_chanel, process_appversion
from states import QuestionsToUser

current_question_num = [10]


def get_question_id(obj):
    res = 0
    with open('questions.json', 'w', encoding='utf-8') as file:
        all_data = json.load(file)
        question = ''
        for k, v in obj.items():
            question = v[:]
        for i, obj in enumerate(all_data):
            if question in obj[i]:
                res = i
    print(res)
    return res


def set_questions(questions):
    res = []
    with open('questions.json', 'w', encoding='utf-8') as f:
        for i, q in enumerate(questions):
            res.append({i: q})
        json.dump(list(res), f, indent=4, ensure_ascii=False)


# def improve_json(msg, path_for_r_file, path_for_w_file, user_front_channel, user_os):
#     with open(f'{path_for_r_file}', 'r',
#               encoding='utf-8') as f_to_r, \
#             open(
#                 f"{path_for_w_file}",
#                 'w', encoding='utf-8') as f_to_w:
#         all_data = json.load(f_to_r)
#
#         res = []
#         for obj in all_data:
#             if obj['FrontChannel'] == user_front_channel:
#                 res.append({
#                     "ID": obj['ID'],
#                     "Service": obj['Service'],
#                     "Operation": obj['Operation'],
#                     "FrontChannel": user_front_channel,
#                     "OS": user_os,
#                     "Question": obj['Question'],
#                     "Steps": obj['Steps']
#                 })
#
#         json.dump(res, f_to_w, indent=4, ensure_ascii=False)


@dp.message_handler(commands=['start'])
async def start(msg: types.Message):
    await bot.send_sticker(msg.from_user.id, 'CAACAgIAAxkBAAEGFT9jSOi4KRAJXIUx29nrBZpE9G_1SAACICEAAsV_QErtb0IwipNsdyoE')
    if not db.user_exists(msg.from_user.id):
        db.add_user(msg.from_user.id)
        await bot.send_message(msg.from_user.id,
                               f'Здравствуйте, {msg.from_user.first_name}!\nЭтот чат-бот создан для консультации и '
                               f'ассистирования пользователей банка '
                               '"Открытие". Для начала ответьте на ряд вопросов.\n'
                               '1. Как вы узнали об этом чат боте?', parse_mode=ParseMode.HTML,
                               reply_markup=markups.choose_where())

        await QuestionsToUser.how_find.set()
    else:
        db.check_param_on_none(msg.from_user.id)

        await bot.send_message(msg.from_user.id,
                               f'Здравствуйте, {msg.from_user.first_name}! Задайте интересующий вас '
                               f'вопрос',
                               reply_markup=markups.main_menu())

    @dp.callback_query_handler(Text(contains='where'), state=QuestionsToUser.how_find)
    async def process_first_q(call: types.CallbackQuery):
        await process_first(call)

    @dp.callback_query_handler(Text(contains='os'), state=QuestionsToUser.user_device)
    async def process_second_q(call):
        await process_second(call)

    @dp.callback_query_handler(Text(startswith='version'), state=QuestionsToUser.appversion)
    async def process_get_appversion(call: types.CallbackQuery, state: FSMContext):
        await process_appversion(call, state)

    @dp.callback_query_handler(Text(startswith='chanel'), state=QuestionsToUser.front_chanel)
    async def process_chanel(call: types.CallbackQuery, state):
        await process_user_chanel(call, state)

    @dp.callback_query_handler(Text('ask'))
    async def ask(call: types.CallbackQuery):
        await bot.delete_message(call.from_user.id, call.message.message_id)
        with open('resources/categories_questions/only_services.json', 'r', encoding='utf-8') as f:
            all_services = json.load(f)
            data = all_services[db.get_user_param(call.from_user.id, 'user_os').lower()]

        await bot.send_message(call.from_user.id, 'Выберите нужный вам сервис',
                               reply_markup=markups.questions_categories(data=data))

    @dp.callback_query_handler(Text(startswith='s'))
    async def get_service(call: types.CallbackQuery):
        service = call.data.split('-')[1]
        user_os = db.get_user_param(call.from_user.id, "user_os")

        user_front_channel = db.get_user_param(call.from_user.id, 'front_chanel')

        with open(
                f'resources/categories_questions/{user_os}/{user_os}_FrontChannel/{user_front_channel}_filt_front_chanel.json',
                'r',
                encoding='utf-8') as f:
            all_data = json.load(f)

            questions = []
            for obj in all_data:
                if obj['Service'] == service:
                    questions.append(obj["Question"])

            set_questions(questions)

            await bot.delete_message(call.from_user.id, call.message.message_id)

            try:
                keyb = InlineKeyboardMarkup(
                    inline_keyboard=[
                        [InlineKeyboardButton(text=q[:50], callback_data=f"poiskchv-{i}")]
                        for i, q in enumerate(list(set(questions)))
                    ]
                )
            except BadRequest:
                keyb = InlineKeyboardMarkup(
                    inline_keyboard=[
                        [InlineKeyboardButton(text=q, callback_data=f"poiskchv-{i}")]
                        for i, q in enumerate(list(set(questions[:100])))
                    ]
                )
            keyb.inline_keyboard.append([InlineKeyboardButton(text='Поддержка', callback_data='contact')])
            keyb.inline_keyboard.append([InlineKeyboardButton(text='В главное меню', callback_data='to_main_menu')])
            await bot.send_message(call.from_user.id,
                                   f'Найдите тут свой вопрос, если его нет, то обратитесь в поддержку',
                                   reply_markup=keyb)

    @dp.callback_query_handler(Text(startswith='poiskchv'))
    async def answer(callback: types.CallbackQuery):
        await bot.delete_message(callback.from_user.id, callback.message.message_id)
        question_id = callback.data.split('-')[1]
        user_os = db.get_user_param(callback.from_user.id, "user_os")

        with open(
                f'resources/questions_answers/questions_answers_{user_os}.json',
                'r', encoding='utf-8') as file, open('questions.json', 'r', encoding='utf-8') as f:
            question = ''
            questions_with_id = json.load(f)

            for q in questions_with_id:
                if question_id in q:
                    question = q[str(question_id)]

            steps = []
            for o in json.load(file):
                if question in o:
                    steps = o[question]

            try:
                await bot.send_message(callback.from_user.id,
                                       f"Ваши действия:\n{'.'.join([f'{i + 1} {s}' for s, i in enumerate(steps)])}",
                                       reply_markup=markups.cumback_to_main_menu)
            except TypeError:
                await bot.send_message(callback.from_user.id,
                                       f"Ваши действия:\n{'.'.join([f'{i} {s}' for s, i in enumerate(steps)])}",
                                       reply_markup=markups.cumback_to_main_menu)


@dp.callback_query_handler(Text('to_main_menu'))
async def to_main_menu(call: types.CallbackQuery):
    await bot.delete_message(call.from_user.id, call.message.message_id)
    await bot.send_message(call.from_user.id, 'Вы вернулись в главное меню', reply_markup=markups.main_menu())


@dp.callback_query_handler(Text('reset_data'))
async def to_main_menu(call: types.CallbackQuery):
    await bot.delete_message(call.from_user.id, call.message.message_id)
    db.reset_data(call.from_user.id)

    await bot.send_message(call.from_user.id, 'Ваш профиль был сброшен. Вы можете создать новый командой /start')


@dp.callback_query_handler(Text('about_us'))
async def about_us(call: types.CallbackQuery):
    await bot.delete_message(call.from_user.id, call.message.message_id)
    await bot.send_message(call.from_user.id, """Банк «Открытие» — универсальный банк с диверсифицированной структурой бизнеса, входит в список системно значимых кредитных организаций, утвержденный Центральным Банком Российской Федерации
Банк «Открытие» входит в топ-10 крупнейших банков России и является системно значимым. Развивает следующие направления бизнеса: корпоративный, инвестиционный, розничный, малый и средний, а также Private banking.
Региональная сеть банка насчитывает 409 клиентских офисов в 200 городах в 73 регионах страны.
Надежность банка подтверждена рейтингами российских агентств АКРА (АА(RU)), Эксперт РА (ruAA), НКР (AA+.ru).""",
                           reply_markup=markups.cumback_to_main_menu)


@dp.callback_query_handler(Text('contact'))
async def contact_with_support(call: types.CallbackQuery):
    await bot.delete_message(call.from_user.id, call.message.message_id)
    await bot.send_message(call.from_user.id, '+78004444400 — Бесплатный звонок по России\n'
                                              '+74952244400 — Для Москвы и звонков из-за границы',
                           reply_markup=markups.cumback_to_main_menu)


@dp.message_handler(content_types=['text'])
async def search(msg: types.Message):
    try:
        user_os = db.get_user_param(msg.from_user.id, 'user_os')
        search_value = msg.text.lower().strip().rstrip()

        with open(f'resources/questions_answers/questions_answers_{user_os}.json', 'r', encoding='utf-8') as file:
            all_data = json.load(file)

            for obj in all_data:
                for k, v in obj.items():
                    joined_items = k.lower()
                    if search_value.lower() in joined_items:
                        await bot.send_message(msg.from_user.id, v)

    except Exception as e:
        print(e)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
