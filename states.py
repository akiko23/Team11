from aiogram.dispatcher.filters.state import StatesGroup, State


class QuestionsToUser(StatesGroup):
    user_device = State()
    how_find = State()
    front_chanel = State()
    appversion = State()


class QuestionFromUser(StatesGroup):
    get_question = State()
    onSearch = State()

