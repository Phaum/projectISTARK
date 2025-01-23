from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton, 
                           InlineKeyboardButton, InlineKeyboardMarkup)



start = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='Начать', callback_data='start')]])

main = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Подтвердить критерии')],
                                     [KeyboardButton(text='Вывести спецификацию текущей котировочной сессии')],
                                     [KeyboardButton(text='Отменить ввод')]],
                                     resize_keyboard=True,
                                     input_field_placeholder='Выберите пункт меню...')

main2 = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Запустить проверку по данной котировочной сессии')],
                                     [KeyboardButton(text='Вывести спецификацию текущей котировочной сессии')],
                                     [KeyboardButton(text='Внести изменения в критерии')],
                                     [KeyboardButton(text='Отменить ввод')]],
                                     resize_keyboard=True,
                                     input_field_placeholder='Выберите пункт меню...')