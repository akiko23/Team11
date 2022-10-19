import json

from aiogram import types
from aiogram.dispatcher.filters import Text
from aiogram.types import ParseMode, KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils import executor

from main_keyb_funcs import *
import markups
from config import dp, bot, db
from get_user_data import set_user_json
from states import QuestionsToUser


@dp.message_handler(commands=['start'])
async def start(msg: types.Message):
    if str(msg.from_user.id) == '5190469004' or str(msg.from_user.id) == '5620749311':
        await bot.send_message(msg.from_user.id, 'Спамерам тут не место!')
    else:
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
            set_user_json(msg)
            await bot.send_message(msg.from_user.id,
                                   f'Здравствуйте, {msg.from_user.first_name}! Задайте интересующий вас '
                                   f'вопрос',
                                   reply_markup=markups.main_menu())


@dp.callback_query_handler(Text('ask'))
async def ask(call: types.CallbackQuery):
    await bot.delete_message(call.from_user.id, call.message.message_id)
    await bot.send_message(call.from_user.id, 'Подождите...')

    with open('resources/current_user_data.json', 'r', encoding='utf-8') as f_to_r:
        all_services = list(set(list(
            map(lambda x: x['Service'] if x is not None else 'NaHn',
                json.load(f_to_r)))))

    await bot.delete_message(call.from_user.id, call.message.message_id + 1)
    await bot.send_message(call.from_user.id, 'Выберите нужный вам сервис',
                           reply_markup=markups.questions_categories(data=all_services))


@dp.message_handler(content_types=['text'])
async def search(msg: types.Message):
    if msg.from_user.id == 5620749311 or msg.from_user.id == 5620749311:
        await bot.send_message(msg.from_user.id, 'Спамерам тут не место!')
    else:
        if not db.user_exists(msg.from_user.id):
            await bot.send_message(msg.from_user.id, 'Для начала пройдите регистрацию')
        else:
            if msg.text == 'Поддержка':
                await bot.delete_message(msg.from_user.id, msg.message_id)
                await bot.send_message(msg.from_user.id, '+78004444400 — Бесплатный звонок по России\n'
                                                         '+74952244400 — Для Москвы и звонков из-за границы',
                                       reply_markup=markups.cumback_to_main_menu)
            elif msg.text == 'В главное меню':
                await bot.delete_message(msg.from_user.id, msg.message_id - 1)
                await bot.delete_message(msg.from_user.id, msg.message_id)
                await bot.send_message(msg.from_user.id, 'Вы вернулись в главное меню', reply_markup=markups.main_menu())

            else:
                try:
                    search_value = msg.text.lower()
                    with open('resources/questions_with_answers/questions_answers.json', 'r', encoding='utf-8') as f_to_r:
                        all_questions_data = filter(lambda x: x is not None, json.load(f_to_r))
                        answers = list(filter(lambda x: search_value in x, all_questions_data))

                        if len(answers) == 0:
                            raise ValueError
                        elif len(answers) > 1:
                            for obj in answers:
                                steps = obj[search_value][0]
                                if 'Version' in obj:
                                    await bot.send_message(msg.from_user.id, f'Для версии {obj["Version"]}\n\n{steps}')
                        else:
                            params = answers[0][search_value]

                            steps = '; '.join([f"{i + 1}. {q}" for i, q in enumerate(params[0])])
                            siteUrls = f'\n\nДополнительная информация:\n {", ".join([url.strip() for url in params[1]])}' if params[
                                                                                         1] is not None else None
                            FAQurls = f'\n\nИ ещё:\n{", ".join([url.strip() for url in params[2]])}' if params[2] is not None else None

                            if siteUrls is None and FAQurls is not None:
                                await bot.send_message(msg.from_user.id, f'Ваши действия:\n\n{steps}\n\n'
                                                                     f'{FAQurls}'
                                                   )
                            if FAQurls is None and siteUrls is not None:
                                await bot.send_message(msg.from_user.id, f'Ваши действия:\n\n{steps}\n\n'
                                                                     f'{siteUrls}'
                                                   )
                            if siteUrls is None and FAQurls is None:
                                await bot.send_message(msg.from_user.id, f'Ваши действия:\n\n{steps}\n\n')

                            else:
                                await bot.send_message(msg.from_user.id, f'Ваши действия:\n\n{steps}\n\n'
                                                                         f'{siteUrls}'
                                                                         f'{FAQurls}'

                                                       )
                except Exception as e:
                    print(f'[INFO]Full value ERROR: {e}')
                    try:
                        search_value = msg.text.lower().strip().rstrip()
                        with open('resources/current_user_data.json', 'r', encoding='utf-8') as f:
                            all_data = list(filter(lambda x: x is not None, json.load(f)))
                            possible_questions = list(
                                filter(lambda x: search_value in ' '.join([x['Service'].lower(), x['Question'].lower()]),
                                       all_data))

                            possible_questions = list(set([obj['Question'] for obj in possible_questions]))
                            possible_questions_keyb = ReplyKeyboardMarkup(
                                keyboard=[[
                                    KeyboardButton(text=q)

                                ] for q in possible_questions])
                            possible_questions_keyb.keyboard.append([KeyboardButton(text='В главное меню')])

                            if len(possible_questions) > 0:
                                await bot.send_message(msg.from_user.id, 'Возможно вы имеете в виду следующие вопросы',
                                                       reply_markup=possible_questions_keyb
                                                       )
                            else:
                                raise IndexError
                    except Exception as e:
                        print(f'Getting possible questions ERROR: {e}')

                        await bot.send_message(msg.from_user.id,
                                               'По вашему запросу ничего не найдено. Попробуйте задать вопрос по '
                                               'конкретным данным в главном меню',
                                               reply_markup=markups.cumback_to_main_menu)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
