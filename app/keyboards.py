from aiogram.types import (
    InlineKeyboardButton, 
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup
)
from aiogram.utils.keyboard import (
    InlineKeyboardBuilder,
    KeyboardBuilder
)



# Reply keyboards

def repl_kb() -> ReplyKeyboardMarkup:
    builder = KeyboardBuilder()

    builder.add(KeyboardButton(text='Template text'))

    return builder.as_markup()



# Inline keyboards

def yes_no_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.add(InlineKeyboardButton(text='yes', callback_data='yes'))
    builder.add(InlineKeyboardButton(text='no', callback_data='no'))

    return builder.as_markup()



# payments

def payment_kb(price) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.row(InlineKeyboardButton(text = f'pay {price} XTR', pay = True))

    return builder.as_markup()
