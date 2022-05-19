from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

btn_main=KeyboardButton('Главное меню')
btn_other=KeyboardButton('Другое')
btn_news=KeyboardButton('Глобальный поиск новостей по тегу')
btn_city=KeyboardButton('поиск новостей по определенному городу')
btn_time=KeyboardButton('поиск новостей по времени')
btn_relevant=KeyboardButton('Релевантные новости')

main_menu=ReplyKeyboardMarkup(resize_keyboard=True).add(btn_news,btn_other)

other_menu=ReplyKeyboardMarkup(resize_keyboard=True).add(btn_city,btn_time,btn_relevant,btn_main)