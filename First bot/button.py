from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton,
                           InlineKeyboardButton, InlineKeyboardMarkup)

main_kb1 = [
    [KeyboardButton(text='Показать список групп')]
    ]
main_kb2 = [
    [KeyboardButton(text='Выбрать группу')]
    ]

main1 = ReplyKeyboardMarkup(keyboard=main_kb1, 
                            resize_keyboard=True)
main2 = ReplyKeyboardMarkup(keyboard=main_kb2, 
                            resize_keyboard=True)

# main_kb = [
#     [KeyboardButton(text='Показать список групп')],
#     [KeyboardButton(text='Выбрать группу')]
#     ]                    
# main = ReplyKeyboardMarkup(keyboard=main_kb, resize_keyboard=True) 

report = InlineKeyboardMarkup(inline_keyboard=[
   [InlineKeyboardButton(text='Отчет', callback_data = 'otchet')]
    ])