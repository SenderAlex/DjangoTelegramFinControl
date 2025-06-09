from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from states import User, RegistrationUser  # Импортируйте ваши состояния
from utils import get_telegram_id, get_telegram_id_by_email, update_telegram_id, create_user  # Импортируйте функции работы с БД

router = Router()


@router.message(F.text == "Регистрация")
async def registration(message: Message, state: FSMContext):
    telegram_id = message.from_user.id
    telegram_db = await get_telegram_id(telegram_id)
    if telegram_db:
        await message.answer("Вы уже зарегистрированы.")
    else:
        await state.set_state(User.email)
        await message.answer('Введите Ваш email')


@router.message(User.email)
async def registration_email(message: Message, state: FSMContext):
    await state.update_data(email=message.text)
    data = await state.get_data()
    telegram_id = message.from_user.id
    email_from_user = data['email']
    user = await get_telegram_id_by_email(email_from_user)

    if user:
        await update_telegram_id(user, telegram_id)
        await message.answer("Ваш телеграм аккаунт успешно сохранен в базу")
    else:
        await message.answer("Пользователь с таким именем не найден!!")
        await message.answer("Вам нужно зарегистрироваться, чтобы пользоваться этим ботом.")
        await state.set_state(RegistrationUser.email)
        await state.update_data(email=email_from_user)
        await state.set_state(RegistrationUser.first_name)
        await message.answer('Введите свое имя')


@router.message(RegistrationUser.first_name)
async def registration_name(message: Message, state: FSMContext):
    await state.update_data(first_name=message.text)
    await state.set_state(RegistrationUser.last_name)
    await message.answer('Введите свою фамилию')


@router.message(RegistrationUser.last_name)
async def registration_surname(message: Message, state: FSMContext):
    await state.update_data(last_name=message.text)
    await state.set_state(RegistrationUser.password)
    await message.answer('Введите пароль для своего аккаунта')


@router.message(RegistrationUser.password)
async def registration_password(message: Message, state: FSMContext):
    await state.update_data(password=message.text)
    data = await state.get_data()
    email = data['email']
    first_name = data['first_name']
    last_name = data['last_name']
    telegram_id = message.from_user.id
    password = data['password']
    user = await create_user(email, first_name, last_name, telegram_id, password)
    await message.answer(f'Пользователь с именем {first_name} успешно зарегистрирован')
    await state.clear()
