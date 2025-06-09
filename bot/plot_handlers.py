from aiogram import Router, F, types
from asgiref.sync import sync_to_async
from aiogram.types.input_file import FSInputFile
from aiogram.fsm.context import FSMContext
from utils import get_user_transactions_async  # Импортируйте функции работы с БД
import os
import pandas as pd
from plot_utils import plot_pie, plot_bar, plot_category_bar
from keaboards import period_choice_keyboard
from states import PeriodSelection
from statistics_handlers import income_statistics, expense_statistics
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fincontrol_project.settings')
django.setup()
from registration_app.models import CustomUser

router = Router()


@router.message(F.text.in_([
    "Статистика по доходам",
    "Статистика по расходам",
    "Гистограмма по доходам",
    "Гистограмма по расходам",
    "Графики доходов по категориям",
    "Графики расходов по категориям",
    "Гистограмма доходов по категориям",
    "Гистограмма расходов по категориям"
]))
async def handle_plot_request(message: types.Message, state: FSMContext):
    # Сохраняем выбранный график в FSM
    await state.update_data(selected_plot=message.text)
    await build_and_send_plot(message, state)


async def build_and_send_plot(message: types.Message, state: FSMContext, start_date: str = None, end_date: str = None):
    data = await state.get_data()
    selected_plot = data.get('selected_plot')
    # Вызов нужной функции по тексту кнопки
    if selected_plot == "Гистограмма по доходам":
        await income_plots(message, start_date, end_date)
    elif selected_plot == "Гистограмма по расходам":
        await expense_plots(message, start_date, end_date)
    elif selected_plot == "Графики доходов по категориям":
        await income_cat_plots(message, start_date, end_date)
    elif selected_plot == "Графики расходов по категориям":
        await expense_cat_plots(message, start_date, end_date)
    elif selected_plot == "Гистограмма доходов по категориям":
        await income_cat_hist(message, start_date, end_date)
    elif selected_plot == "Гистограмма расходов по категориям":
        await expense_cat_hist(message, start_date, end_date)
    elif selected_plot == "Статистика по доходам":
        await income_statistics(message, start_date, end_date)
    elif selected_plot == "Статистика по расходам":
        await expense_statistics(message, start_date, end_date)
    else:
        await message.answer("Не удалось определить тип графика или данных.")


@router.callback_query(F.data == "choose_period")
async def ask_start_date(callback_query: types.CallbackQuery, state: FSMContext):
    await state.set_state(PeriodSelection.waiting_for_start_date)
    await callback_query.message.answer("Введите начальную дату (ГГГГ-ММ-ДД):")
    await callback_query.answer()


@router.callback_query(F.data == "all_period")
async def keep_all_period(callback_query: types.CallbackQuery):
    await callback_query.message.answer("График оставлен без изменений.")
    await callback_query.answer()


# --- FSM: ввод дат ---

@router.message(PeriodSelection.waiting_for_start_date)
async def get_start_date(message: types.Message, state: FSMContext):
    await state.update_data(start_date=message.text)
    await state.set_state(PeriodSelection.waiting_for_end_date)
    await message.answer("Введите конечную дату (ГГГГ-ММ-ДД):")


@router.message(PeriodSelection.waiting_for_end_date)
async def get_end_date(message: types.Message, state: FSMContext):
    await state.update_data(end_date=message.text)
    data = await state.get_data()
    start_date = data.get('start_date')
    end_date = data.get('end_date')
    # Вызываем универсальный обработчик, который сам выберет нужную функцию
    await build_and_send_plot(message, state, start_date, end_date)
    await state.clear()


async def income_plots(message: types.Message, start_date: str = None, end_date: str = None):
    user_telegram_id = message.from_user.id

    if not user_telegram_id:
        await message.answer("Сначала зарегистрируйтесь.")
        return

    user_obj = await sync_to_async(CustomUser.objects.get)(telegram_id=user_telegram_id)
    transactions = await get_user_transactions_async(user_obj)

    # Подготовка данных
    data = {
        'date': [transaction.date.date() for transaction in transactions],
        'amount': [transaction.amount for transaction in transactions],
        'type': [transaction.type for transaction in transactions],
    }

    df = pd.DataFrame(data)

    # Конвертация столбца date в datetime (если это не так)
    df['date'] = pd.to_datetime(df['date'])

    # Если заданы даты, фильтруем DataFrame по диапазону
    if start_date and end_date:
        try:
            start = pd.to_datetime(start_date)
            end = pd.to_datetime(end_date)
            df = df.loc[(df['date'] >= start) & (df['date'] <= end)]
        except Exception as e:
            await message.answer("Ошибка в формате даты. Используйте ГГГГ-ММ-ДД.")
            return



    # Группировка данных и суммирование по датам
    daily_income_sums = df[df['type'] == 'income'].groupby('date')['amount'].sum()
    daily_income_sums = pd.to_numeric(daily_income_sums, errors='coerce').dropna()

    # Путь к директории с текущим скриптом
    base_dir = os.path.dirname(os.path.abspath(__file__))

    # Путь к файлу с фото в той же папке
    if not daily_income_sums.empty:
        daily_income_values_bar = plot_bar(daily_income_sums, 'Суммы транзакций (доходов) по датам', 'Дата', 'Сумма')
        photo_path_income_bar = os.path.join(base_dir, daily_income_values_bar)  # замените your_photo.png на имя вашего файла
        photo_income_bar = FSInputFile(photo_path_income_bar)
        await message.answer_photo(photo=photo_income_bar)
        await message.answer("Отобразить график за выбранный период?", reply_markup=period_choice_keyboard())
        os.remove(daily_income_values_bar)
    else:
        await message.answer("Нет данных по доходам для построения гистограмм.")


async def expense_plots(message: types.Message, start_date: str = None, end_date: str = None):
    user_telegram_id = message.from_user.id

    if not user_telegram_id:
        await message.answer("Сначала зарегистрируйтесь.")
        return

    user_obj = await sync_to_async(CustomUser.objects.get)(telegram_id=user_telegram_id)
    transactions = await get_user_transactions_async(user_obj)

    # Подготовка данных
    data = {
        'date': [transaction.date.date() for transaction in transactions],
        'amount': [transaction.amount for transaction in transactions],
        'type': [transaction.type for transaction in transactions],
    }

    df = pd.DataFrame(data)

    # Конвертация столбца date в datetime (если это не так)
    df['date'] = pd.to_datetime(df['date'])

    # Если заданы даты, фильтруем DataFrame по диапазону
    if start_date and end_date:
        try:
            start = pd.to_datetime(start_date)
            end = pd.to_datetime(end_date)
            df = df.loc[(df['date'] >= start) & (df['date'] <= end)]
        except Exception as e:
            await message.answer("Ошибка в формате даты. Используйте ГГГГ-ММ-ДД.")
            return


    # Группировка данных и суммирование по датам
    daily_expense_sums = df[df['type'] == 'expense'].groupby('date')['amount'].sum()
    daily_expense_sums = pd.to_numeric(daily_expense_sums, errors='coerce').dropna()

    # Путь к директории с текущим скриптом
    base_dir = os.path.dirname(os.path.abspath(__file__))

    # Путь к файлу с фото в той же папке
    if not daily_expense_sums.empty:
        daily_expense_values_bar = plot_bar(daily_expense_sums, 'Суммы транзакций (расходов) по датам', 'Дата', 'Сумма')
        photo_path_expense_bar = os.path.join(base_dir, daily_expense_values_bar)  # замените your_photo.png на имя вашего файла
        photo_expense_bar = FSInputFile(photo_path_expense_bar)
        await message.answer_photo(photo=photo_expense_bar)
        await message.answer("Отобразить график за выбранный период?", reply_markup=period_choice_keyboard())
        os.remove(daily_expense_values_bar)
    else:
        await message.answer("Нет данных по расходам для построения гистограмм.")


async def income_cat_plots(message: types.Message, start_date: str = None, end_date: str = None):
    user_telegram_id = message.from_user.id

    if not user_telegram_id:
        await message.answer("Сначала зарегистрируйтесь.")
        return

    user_obj = await sync_to_async(CustomUser.objects.get)(telegram_id=user_telegram_id)
    transactions = await get_user_transactions_async(user_obj)

    # Подготовка данных
    data = {
        'date': [transaction.date.date() for transaction in transactions],
        'amount': [transaction.amount for transaction in transactions],
        'type': [transaction.type for transaction in transactions],
        'category__name': [transaction.category.name for transaction in transactions]
    }
    df = pd.DataFrame(data)

    # Конвертация столбца date в datetime (если это не так)
    df['date'] = pd.to_datetime(df['date'])

    # Если заданы даты, фильтруем DataFrame по диапазону
    if start_date and end_date:
        try:
            start = pd.to_datetime(start_date)
            end = pd.to_datetime(end_date)
            df = df.loc[(df['date'] >= start) & (df['date'] <= end)]
        except Exception as e:
            await message.answer("Ошибка в формате даты. Используйте ГГГГ-ММ-ДД.")
            return

    # Путь к директории с текущим скриптом
    base_dir = os.path.dirname(os.path.abspath(__file__))

    income_cat = df[df['type'] == 'income'].groupby('category__name')['amount'].sum()
    income_cat = pd.to_numeric(income_cat, errors='coerce').dropna()
    income_cat.name = None

    if not income_cat.empty:
        img_income_pie = plot_pie(income_cat, 'Доходы (круговая диаграмма)') if not income_cat.empty else None
        photo_path_income = os.path.join(base_dir, img_income_pie)
        photo_income = FSInputFile(photo_path_income)
        await message.answer_photo(photo=photo_income)
        await message.answer("Отобразить график за выбранный период?", reply_markup=period_choice_keyboard())
        os.remove(img_income_pie)
    else:
        await message.answer("Нет данных по доходам для построения графика.")


async def expense_cat_plots(message: types.Message, start_date: str = None, end_date: str = None):
    user_telegram_id = message.from_user.id

    if not user_telegram_id:
        await message.answer("Сначала зарегистрируйтесь.")
        return

    user_obj = await sync_to_async(CustomUser.objects.get)(telegram_id=user_telegram_id)
    transactions = await get_user_transactions_async(user_obj)

    # Подготовка данных
    data = {
        'date': [transaction.date.date() for transaction in transactions],
        'amount': [transaction.amount for transaction in transactions],
        'type': [transaction.type for transaction in transactions],
        'category__name': [transaction.category.name for transaction in transactions]
    }
    df = pd.DataFrame(data)

    # Конвертация столбца date в datetime (если это не так)
    df['date'] = pd.to_datetime(df['date'])

    # Если заданы даты, фильтруем DataFrame по диапазону
    if start_date and end_date:
        try:
            start = pd.to_datetime(start_date)
            end = pd.to_datetime(end_date)
            df = df.loc[(df['date'] >= start) & (df['date'] <= end)]
        except Exception as e:
            await message.answer("Ошибка в формате даты. Используйте ГГГГ-ММ-ДД.")
            return

    # Путь к директории с текущим скриптом
    base_dir = os.path.dirname(os.path.abspath(__file__))

    expense_cat = df[df['type'] == 'expense'].groupby('category__name')['amount'].sum()
    expense_cat = pd.to_numeric(expense_cat, errors='coerce').dropna()
    expense_cat.name = None

    if not expense_cat.empty:
        img_expense_pie = plot_pie(expense_cat, 'Расходы (круговая диаграмма)') if not expense_cat.empty else None
        photo_path_expense = os.path.join(base_dir, img_expense_pie)
        photo_expense = FSInputFile(photo_path_expense)
        await message.answer_photo(photo=photo_expense)
        await message.answer("Отобразить график за выбранный период?", reply_markup=period_choice_keyboard())
        os.remove(img_expense_pie)
    else:
        await message.answer("Нет данных по расходам для построения графика.")


async def income_cat_hist(message: types.Message, start_date: str = None, end_date: str = None):
    user_telegram_id = message.from_user.id

    if not user_telegram_id:
        await message.answer("Сначала зарегистрируйтесь.")
        return

    user_obj = await sync_to_async(CustomUser.objects.get)(telegram_id=user_telegram_id)
    transactions = await get_user_transactions_async(user_obj)

    # Подготовка данных
    data = {
        'date': [transaction.date.date() for transaction in transactions],
        'amount': [transaction.amount for transaction in transactions],
        'type': [transaction.type for transaction in transactions],
        'category__name': [transaction.category.name for transaction in transactions]
    }
    df = pd.DataFrame(data)

    # Конвертация столбца date в datetime (если это не так)
    df['date'] = pd.to_datetime(df['date'])

    # Если заданы даты, фильтруем DataFrame по диапазону
    if start_date and end_date:
        try:
            start = pd.to_datetime(start_date)
            end = pd.to_datetime(end_date)
            df = df.loc[(df['date'] >= start) & (df['date'] <= end)]
        except Exception as e:
            await message.answer("Ошибка в формате даты. Используйте ГГГГ-ММ-ДД.")
            return

    income_cat_date = df[df['type'] == 'income'].pivot_table(
        index='date', columns='category__name', values='amount', aggfunc='sum', fill_value=0)
    income_cat_date = income_cat_date.apply(pd.to_numeric, errors='coerce').fillna(0)

    # Путь к директории с текущим скриптом
    base_dir = os.path.dirname(os.path.abspath(__file__))

    if not income_cat_date.empty:
        img_cat_income_hist = plot_category_bar(income_cat_date, 'Доходы по категориям в разрезе дней', 'Дата', 'Сумма')\
            if not income_cat_date.empty else None
        photo_path_cat_income = os.path.join(base_dir, img_cat_income_hist)
        photo_cat_income = FSInputFile(photo_path_cat_income)
        await message.answer_photo(photo=photo_cat_income)
        await message.answer("Отобразить график за выбранный период?", reply_markup=period_choice_keyboard())
        os.remove(img_cat_income_hist)
    else:
        await message.answer("Нет данных по категориальным доходам для построения графика.")


async def expense_cat_hist(message: types.Message, start_date: str = None, end_date: str = None):
    user_telegram_id = message.from_user.id

    if not user_telegram_id:
        await message.answer("Сначала зарегистрируйтесь.")
        return

    user_obj = await sync_to_async(CustomUser.objects.get)(telegram_id=user_telegram_id)
    transactions = await get_user_transactions_async(user_obj)

    # Подготовка данных
    data = {
        'date': [transaction.date.date() for transaction in transactions],
        'amount': [transaction.amount for transaction in transactions],
        'type': [transaction.type for transaction in transactions],
        'category__name': [transaction.category.name for transaction in transactions]
    }
    df = pd.DataFrame(data)

    # Конвертация столбца date в datetime (если это не так)
    df['date'] = pd.to_datetime(df['date'])

    # Если заданы даты, фильтруем DataFrame по диапазону
    if start_date and end_date:
        try:
            start = pd.to_datetime(start_date)
            end = pd.to_datetime(end_date)
            df = df.loc[(df['date'] >= start) & (df['date'] <= end)]
        except Exception as e:
            await message.answer("Ошибка в формате даты. Используйте ГГГГ-ММ-ДД.")
            return

    expense_cat_date = df[df['type'] == 'expense'].pivot_table(
        index='date', columns='category__name', values='amount', aggfunc='sum', fill_value=0)
    expense_cat_date = expense_cat_date.apply(pd.to_numeric, errors='coerce').fillna(0)

    # Путь к директории с текущим скриптом
    base_dir = os.path.dirname(os.path.abspath(__file__))

    if not expense_cat_date.empty:
        img_cat_expense_hist = plot_category_bar(expense_cat_date, 'Расходы по категориям в разрезе дней', 'Дата', 'Сумма')\
            if not expense_cat_date.empty else None
        photo_path_cat_expense = os.path.join(base_dir, img_cat_expense_hist)
        photo_cat_expense = FSInputFile(photo_path_cat_expense)
        await message.answer_photo(photo=photo_cat_expense)
        await message.answer("Отобразить график за выбранный период?", reply_markup=period_choice_keyboard())
        os.remove(img_cat_expense_hist)
    else:
        await message.answer("Нет данных по категориальным расходам для построения графика.")

