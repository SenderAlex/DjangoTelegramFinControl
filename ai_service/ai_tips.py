import requests
from .config_ai import AI_TOKEN, FOLDER_ID


def get_financial_advice_from_yandexgpt(income_history_text, expense_history_text):
    url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
    headers = {
        "Authorization": f"Api-Key {AI_TOKEN}",
        "Content-Type": "application/json"
    }
    data = {
        "modelUri": f"gpt://{FOLDER_ID}/yandexgpt/latest",
        "completionOptions": {
            "stream": False,
            "temperature": 0.7,
            "maxTokens": 700
        },
        "messages": [
            {"role": "system", "text": "Ты финансовый консультант."},
            {"role": "user", "text": (
        f"На основе истории трат и заработка пользователя дай раздельные советы:\n"
        f"1. Советы по управлению расходами:\n{expense_history_text}\n\n"
        f"2. Советы по увеличению или оптимизации доходов:\n{income_history_text}"
            )}
        ]
    }
    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        response.raise_for_status()
        result = response.json()
        # Извлечение ответа
        return result['result']['alternatives'][0]['message']['text']
    except requests.exceptions.HTTPError as e:
        return f"Ошибка YandexGPT API: {str(e)}"
    except Exception as e:
        return f"Произошла непредвиденная ошибка: {str(e)}"