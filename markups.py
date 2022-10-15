from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.exceptions import ButtonDataInvalid


def main_menu():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton('Задать вопрос', callback_data='ask'),
                InlineKeyboardButton('О нас', callback_data='about_us')
            ],
            [
                InlineKeyboardButton('Связаться с оператором', callback_data='contact'),
                InlineKeyboardButton('Сбросить параметры', callback_data='reset_data')
            ],
        ]
    )


cumback_to_main_menu = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='В главное меню', callback_data='to_main_menu')]
    ]
)


def operations_keyb(operations):
    keyb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=operation, callback_data=f'op-{i}')]
            for i, operation in enumerate(operations[0])
        ]
    )
    keyb.inline_keyboard.append([InlineKeyboardButton(text='В главное меню', callback_data='to_main_menu')])
    return keyb


def questions(possible_questions):
    keyb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=q + '?', callback_data=f"q-{i}")]
            for i, q in enumerate(possible_questions)
        ]
    )
    keyb.inline_keyboard.append([InlineKeyboardButton(text='В главное меню', callback_data='to_main_menu')])
    return keyb


def questions_categories(data):
    keyboard = ReplyKeyboardMarkup()
    for i, c in enumerate(data):
        try:
            if c != 'NaHn':
                keyboard.keyboard.append([
                    KeyboardButton(text=c)
                ])
            else:
                continue
        except IndexError:
            continue
    keyboard.keyboard.append(
        [
            KeyboardButton(text='В главное меню', callback_data='to_main_menu')
        ]
    )
    return keyboard


def choose_where():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton('C сайта', callback_data='where-site'),
                InlineKeyboardButton('Социальные сети', callback_data='where-socialmedia'),
            ],
            [
                InlineKeyboardButton('От знакомых', callback_data='where-familiar'),
                InlineKeyboardButton('Из рекламы', callback_data='where-advertisement')
            ]
        ],

    )
    return keyboard


def onchoose_os():
    advertisement_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton('Apple', callback_data='os-iOS'),
                InlineKeyboardButton('Android', callback_data='os-Android'),
            ]
        ]
    )
    return advertisement_keyboard
