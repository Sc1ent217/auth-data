import asyncio
import time
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart

TOKEN = os.environ.get("TOKEN")

ADMIN_ID = 1691409962
CHANNEL_ID = -1003808866046
DELAY = 20

bot = Bot(token=TOKEN)
dp = Dispatcher()

last_message_time = {}
wait_tasks = {}

@dp.message(CommandStart())
async def start(message: types.Message):
    await message.answer(
        f"✉️ Отправь сообщение — оно анонимно появится в канале.\n"
        f"⏳ Задержка: {DELAY} сек."
    )

async def notify_ready(user_id: int):
    await asyncio.sleep(DELAY)
    await bot.send_message(user_id, "✅ Теперь можно отправлять сообщение")
    wait_tasks.pop(user_id, None)

@dp.message()
async def handle_message(message: types.Message):
    user_id = message.from_user.id
    username = message.from_user.username or "Без юзернейма"
    now = time.time()

    if user_id in last_message_time and (elapsed := now - last_message_time[user_id]) < DELAY:
        await message.answer(f"⏳ Подожди {int(DELAY - elapsed)} сек.")
        if user_id not in wait_tasks:
            wait_tasks[user_id] = asyncio.create_task(notify_ready(user_id))
        return

    last_message_time[user_id] = now

    msg_text = f"Сообщение от @{username}:\n\n" + (message.text or "Медиа")
    await bot.send_message(ADMIN_ID, msg_text)

    if message.text:
        await bot.send_message(CHANNEL_ID, message.text)
    elif message.photo:
        await bot.send_photo(CHANNEL_ID, message.photo[-1].file_id)
    elif message.video:
        await bot.send_video(CHANNEL_ID, message.video.file_id)
    elif message.voice:
        await bot.send_voice(CHANNEL_ID, message.voice.file_id)

    await message.answer("✅ Сообщение отправлено")

async def main():
    print("✅ Бот запущен")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
