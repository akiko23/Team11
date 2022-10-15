from aiogram import types
from aiogram.dispatcher.filters import Text

import markups
from config import dp, db, bot


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