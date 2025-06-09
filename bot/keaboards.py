from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

button_registr = KeyboardButton(text="Регистрация")
button_voice_data = KeyboardButton(text="Голосовой ввод данных")
button_statistics_income = KeyboardButton(text="Статистика по доходам")
button_statistics_expense = KeyboardButton(text="Статистика по расходам")
button_hist_income = KeyboardButton(text="Гистограмма по доходам")
button_hist_expense = KeyboardButton(text="Гистограмма по расходам")
button_category_plots_income = KeyboardButton(text="Графики доходов по категориям")
button_category_plots_expense = KeyboardButton(text="Графики расходов по категориям")
button_category_hist_income = KeyboardButton(text="Гистограмма доходов по категориям")
button_category_hist_expense = KeyboardButton(text="Гистограмма расходов по категориям")


keyboards = ReplyKeyboardMarkup(keyboard=[
    [button_registr, button_voice_data],
    [button_statistics_income, button_statistics_expense, button_hist_income, button_hist_expense],
    [button_category_plots_income, button_category_plots_expense, button_category_hist_income,
     button_category_hist_expense],
    ], resize_keyboard=True)