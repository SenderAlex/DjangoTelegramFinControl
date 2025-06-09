from aiogram.fsm.state import StatesGroup, State


class User(StatesGroup):
    email = State()


class RegistrationUser(StatesGroup):
    email = State()
    first_name = State()
    last_name = State()
    password = State()


class PeriodSelection(StatesGroup):
    waiting_for_start_date = State()
    waiting_for_end_date = State()


class VoiceInput(StatesGroup):
    waiting_for_voice = State()
