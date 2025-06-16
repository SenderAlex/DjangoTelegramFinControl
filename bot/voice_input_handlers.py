from aiogram import Router, F, types
from states import VoiceInput
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
import os
from voice_input_data import parse_transaction, save_transaction
import whisper
from bot_instance import bot

import sys
ffmpeg_path = r"C:\Работа\Python_with_ChatGPT\Модуль_1\Урок_77 Итоговый проект\DjangoTelegramFinControl\ffmpeg\bin"
os.environ["PATH"] += os.pathsep + ffmpeg_path

router = Router()

model = whisper.load_model("base")


@router.message(F.text == "Голосовой ввод данных")
async def voice_input_data(message: Message, state: FSMContext):
    await message.answer('Пожалуйста, отправьте голосовое сообщение по следующему шаблону: "доход 500 зарплата от работы".')
    await state.set_state(VoiceInput.waiting_for_voice)


@router.message(F.content_type == types.ContentType.VOICE)
async def handle_voice(message: Message, state: FSMContext):
    # 1. Скачиваем и конвертируем голосовое сообщение
    file_info = await bot.get_file(message.voice.file_id)
    voice_file = await bot.download_file(file_info.file_path)
    ogg_path = f"voice_{message.from_user.id}.ogg"
    wav_path = f"voice_{message.from_user.id}.wav"

    with open(ogg_path, "wb") as f:
        f.write(voice_file.read())

    from pydub import AudioSegment
    audio = AudioSegment.from_ogg(ogg_path)
    audio.export(wav_path, format="wav")

    # 2. Распознаём речь
    result = model.transcribe(wav_path)
    text = result["text"]

    # 3. Парсим текст
    parsed = parse_transaction(text)
    if all(parsed.values()):
        # 4. Сохраняем в базу
        await save_transaction(
            user_id=message.from_user.id,
            type_=parsed['type'],
            amount=parsed['amount'],
            category=parsed['category'],
            description=parsed['description']
        )
        await message.reply("Транзакция успешно добавлена!")
    else:
        await message.reply("Не удалось распознать все параметры. Пожалуйста, повторите ввод.")

    os.remove(ogg_path)
    os.remove(wav_path)
    await state.clear()