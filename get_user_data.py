import json

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

import markups
from config import bot, db, dp
from states import QuestionsToUser


def sort_by_user_os(x, user_os):
    if 'OS' in x and (x['OS'] == user_os or x['OS'] == 'All' or x['OS'] is None):
        return True
    else:
        return False


def sort_by_user_front_chanel(x, user_front_channel):
    if 'FrontChannel' in x and x['FrontChannel'] == user_front_channel:
        return True
    else:
        return False


def set_user_json(msg):
    data_status = db.get_user_param(msg.from_user.id, 'data_load_status')
    if not data_status:
        user_os = db.get_user_param(msg.from_user.id, 'user_os')
        user_front_channel = db.get_user_param(msg.from_user.id, 'front_chanel')

        with open(f"resources/normal_answers.json", 'r', encoding='utf-8') as file, \
                open('resources/current_user_data.json', 'w', encoding='utf-8') as f_to_w:
            all_data = json.load(file)

            sorted_data_by_userOS = list(
                map(lambda x: x if sort_by_user_os(x, user_os) and sort_by_user_front_chanel(x,
                                                                                             user_front_channel) else None,
                    all_data))
            json.dump(sorted_data_by_userOS, f_to_w, indent=4, ensure_ascii=False)

            db.set_user_data(msg.from_user.id, 'data_load_status', True)
    else:
        pass


def set_user_questions_answers():
    with open('resources/current_user_data.json', 'r', encoding='utf-8') as f_to_r, \
            open('resources/questions_with_answers/questions_answers.json', 'w', encoding='utf-8') as f_to_w:
        all_data = json.load(f_to_r)
        res = []

        for obj in all_data:
            if obj is not None:
                res.append({
                    "ID": int(obj['ID']),
                    'Service': obj['Service'],
                    'Version': obj['Version'] if 'Version' in obj else None,
                    obj['Question'].lower(): [obj['Steps'], obj['FAQUrls'], obj['SiteUrl']]
                })
        json.dump(res, f_to_w, indent=4, ensure_ascii=False)


@dp.callback_query_handler(Text(contains='where'), state=QuestionsToUser.how_find)
async def process_first_q(call: types.CallbackQuery):
    await bot.delete_message(message_id=call.message.message_id, chat_id=call.from_user.id)
    value = call.data.split('-')[1]

    db.set_user_data(call.from_user.id, 'how_find', value)

    await bot.send_message(call.from_user.id, '2. Какой вы используете банк?',
                           reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                               [
                                   InlineKeyboardButton(text='Мобильный', callback_data='chanel-МБ'),
                                   InlineKeyboardButton(text="Интернет", callback_data='chanel-ИБ')
                               ]
                           ]))
    await QuestionsToUser.front_chanel.set()


@dp.callback_query_handler(Text(contains='os'), state=QuestionsToUser.user_device)
async def process_second_q(call: types.CallbackQuery, state):
    await bot.delete_message(message_id=call.message.message_id, chat_id=call.from_user.id)
    os = call.data.split('-')[1]

    db.set_user_data(call.from_user.id, 'user_os', os)

    await bot.send_message(call.from_user.id, '⏳Производится обработка...')
    set_user_json(call)
    set_user_questions_answers()
    await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id + 1)

    await bot.send_message(call.from_user.id,
                           'Спасибо за ваши ответы, теперь можете задать вопрос в главном меню',
                           reply_markup=markups.cumback_to_main_menu)

    await state.finish()


@dp.callback_query_handler(Text(startswith='chanel'), state=QuestionsToUser.front_chanel)
async def process_chanel(call: types.CallbackQuery):
    await bot.delete_message(message_id=call.message.message_id, chat_id=call.from_user.id)

    front_chanel = call.data.split('-')[1]
    db.set_user_data(call.from_user.id, 'front_chanel', front_chanel)

    await bot.send_message(call.from_user.id, '3. С какого устройства вы запустили этого чат бота?',
                           reply_markup=markups.onchoose_os())
    await QuestionsToUser.user_device.set()
