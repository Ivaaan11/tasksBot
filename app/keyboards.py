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


def menu_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    
    builder.button(text='Main menu', callback_data='main_menu')
    builder.button(text='Add a new task', callback_data='add_task')
    builder.button(text='View your tasks', callback_data='view_tasks')
    builder.button(text='Delete a task', callback_data='delete_task')
    builder.button(text='Edit a task', callback_data='edit_task')

    return builder.adjust(2).as_markup()



# payments

def payment_kb(price) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.row(InlineKeyboardButton(text = f'pay {price} XTR', pay = True))

    return builder.as_markup()
