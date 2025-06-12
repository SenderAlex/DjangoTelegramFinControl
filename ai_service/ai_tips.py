from openai import OpenAI
from openai import RateLimitError, OpenAIError
from .config_ai import AI_TOKEN


client = OpenAI(api_key=AI_TOKEN)


def get_financial_advice_from_chatgpt(expense_history_text):
    messages = [
        {"role": "system", "content": "Ты финансовый консультант."},
        {"role": "user", "content": f"На основе истории трат пользователя дай советы:\n{expense_history_text}"}
    ]

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # или "gpt-3.5-turbo"
            messages=messages,
            max_tokens=700,
            temperature=0.7,
        )
        return response.choices[0].message.content
    except RateLimitError:
        return "Превышен лимит запросов к AI. Попробуйте позже."
    except OpenAIError as e:
        return f"Ошибка OpenAI API: {str(e)}"
    except Exception as e:
        return f"Произошла непредвиденная ошибка: {str(e)}"

