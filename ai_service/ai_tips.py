import os
import openai
from config_ai import AI_TOKEN


openai.api_key = os.getenv(AI_TOKEN)


def get_financial_advice_from_chatgpt(expense_history_text):
    prompt = (
        "Ты финансовый консультант. На основе истории трат пользователя дай практические советы по экономии и идеям для заработка.\n"
        f"История трат:\n{expense_history_text}\n"
        "Дай рекомендации простым и понятным языком."
    )
    response = openai.ChatCompletion.create(
        model="gpt-4",  # или "gpt-3.5-turbo"
        messages=[
            {"role": "system", "content": "Ты финансовый консультант."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=700,
        temperature=0.7,
    )
    return response.choices[0].message.content
