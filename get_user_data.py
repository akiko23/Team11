from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

import markups
from config import bot, db, dp
from states import QuestionsToUser


async def process_first(call: types.CallbackQuery):
    await bot.delete_message(message_id=call.message.message_id, chat_id=call.from_user.id)
    value = call.data.split('-')[1]

    db.set_user_data(call.from_user.id, 'how_find', value)

    await bot.send_message(call.from_user.id, '2. С какого устройства вы запустили этого чат бота?',
                           reply_markup=markups.onchoose_os())
    await QuestionsToUser.user_device.set()


async def process_second(call: types.CallbackQuery):
    await bot.delete_message(message_id=call.message.message_id, chat_id=call.from_user.id)

    os = call.data.split('-')[1]
    db.set_user_data(call.from_user.id, 'user_os', os)

    await bot.send_message(call.from_user.id, '3. Какой вы используете банк?',
                           reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                               [
                                   InlineKeyboardButton(text='Мобильный', callback_data='chanel-МБ'),
                                   InlineKeyboardButton(text="Интернет", callback_data='chanel-ИБ')
                               ]
                           ]))
    await QuestionsToUser.front_chanel.set()


async def process_user_chanel(call: types.CallbackQuery, state: FSMContext):
    await bot.delete_message(message_id=call.message.message_id, chat_id=call.from_user.id)

    front_chanel = call.data.split('-')[1]
    db.set_user_data(call.from_user.id, 'front_chanel', front_chanel)

    if front_chanel == 'MB':
        await bot.send_message(call.from_user.id, '4. Выберите версию вашего мобильного банка',
                               reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                                   [
                                       InlineKeyboardButton(text="2.62", callback_data='version-2.62'),
                                       InlineKeyboardButton(text="2.69", callback_data='version-2.69'),
                                       InlineKeyboardButton(text="2.70", callback_data='version-2.70'),
                                   ]
                               ]))
        await QuestionsToUser.appversion.set()
    else:
        await bot.send_message(call.from_user.id, 'Спасибо за ваши ответы, теперь можете задать вопрос в главном меню',
                               reply_markup=markups.cumback_to_main_menu)
        await state.finish()


async def process_appversion(call: types.CallbackQuery, state: FSMContext):
    await bot.delete_message(message_id=call.message.message_id, chat_id=call.from_user.id)

    db.set_user_data(call.from_user.id, column_name='app_version', value=call.data.split('-')[1])

    await bot.send_message(call.from_user.id, 'Спасибо за ваши ответы, теперь можете задать вопрос в главном меню',
                           reply_markup=markups.cumback_to_main_menu)
    await state.finish()

