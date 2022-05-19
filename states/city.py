from aiogram.dispatcher.filters.state import StatesGroup, State

class Select_City(StatesGroup):
    city_set = State()
