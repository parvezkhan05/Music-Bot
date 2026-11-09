[09.11.2026 22:35] Parvez Anvarov: import asyncio
import os
import aiohttp

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
raise RuntimeError("BOT_TOKEN topilmadi!")

bot = Bot(token=TOKEN)
dp = Dispatcher()

users = set()
languages = {}

TEXTS = {
"uz": {
"welcome": "🎵 VKM UZ BOT ga xush kelibsiz!\n\nMusiqa nomini yuboring yoki menyudan foydalaning.",
"music": "🎵 Musiqa nomini yozing:",
"video": "🎬 Video qidirish uchun nomini yozing:",
"language": "🌐 Tilni tanlang:",
"help": "Bot orqali musiqa qidirishingiz va havolalarni tekshirishingiz mumkin.",
"not_found": "Natija topilmadi."
},
"ru": {
"welcome": "🎵 Добро пожаловать в VKM UZ BOT!\n\nОтправьте название музыки или выберите меню.",
"music": "🎵 Напишите название музыки:",
"video": "🎬 Напишите название видео:",
"language": "🌐 Выберите язык:",
"help": "Бот позволяет искать музыку и проверять ссылки.",
"not_found": "Ничего не найдено."
}
}

def get_lang(user_id):
return languages.get(user_id, "uz")

def menu(lang):
if lang == "ru":
return InlineKeyboardMarkup(inline_keyboard=[
[InlineKeyboardButton(text="🎵 Музыка", callback_data="music")],
[InlineKeyboardButton(text="🎬 Видео", callback_data="video")],
[InlineKeyboardButton(text="🌐 Язык", callback_data="language")]
])
return InlineKeyboardMarkup(inline_keyboard=[
[InlineKeyboardButton(text="🎵 Musiqa", callback_data="music")],
[InlineKeyboardButton(text="🎬 Video", callback_data="video")],
[InlineKeyboardButton(text="🌐 Til", callback_data="language")]
])

@dp.message(Command("start"))
async def start(message: Message):
users.add(message.from_user.id)
lang = get_lang(message.from_user.id)
await message.answer(TEXTS[lang]["welcome"], reply_markup=menu(lang))

@dp.message(Command("help"))
async def help_command(message: Message):
lang = get_lang(message.from_user.id)
await message.answer(TEXTS[lang]["help"])

@dp.message(Command("stats"))
async def stats(message: Message):
await message.answer(f"👥 Foydalanuvchilar: {len(users)}")

@dp.callback_query(F.data == "music")
async def music_button(callback):
lang = get_lang(callback.from_user.id)
await callback.message.answer(TEXTS[lang]["music"])
await callback.answer()

@dp.callback_query(F.data == "video")
async def video_button(callback):
lang = get_lang(callback.from_user.id)
await callback.message.answer(TEXTS[lang]["video"])
await callback.answer()

@dp.callback_query(F.data == "language")
async def language_button(callback):
keyboard = InlineKeyboardMarkup(inline_keyboard=[
[InlineKeyboardButton(text="🇺🇿 O‘zbekcha", callback_data="lang_uz")],
[InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_ru")]
])
await callback.message.answer("Til / Язык:", reply_markup=keyboard)
await callback.answer()

@dp.callback_query(F.data.startswith("lang_"))
async def set_language(callback):
lang = callback.data.split("_")[1]
languages[callback.from_user.id] = lang
await callback.message.answer(TEXTS[lang]["welcome"], reply_markup=menu(lang))
await callback.answer()

@dp.message(F.text)
async def search_music(message: Message):
users.add(message.from_user.id)
lang = get_lang(message.from_user.id)
query = message.text.strip()

if query.startswith(("http://", "https://")):
    await message.answer(
        "🔗 Havola qabul qilindi. Hozircha bu prototip havolani tekshirish bilan cheklanadi."
    )
    return

await message.answer("🔎 Qidirilmoqda...")

url = "https://itunes.apple.com/search"
params = {"term": query, "entity": "song", "limit": 5}

try:
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as response:
            data = await response.json()

    results = data.get("results", [])

    if not results:
        await message.answer(TEXTS[lang]["not_found"])
        return

    for track in results:
        title = track.get("trackName", "Noma'lum")
        artist = track.get("artistName", "Noma'lum")
        preview = track.get("previewUrl")
[09.11.2026 22:35] Parvez Anvarov: link = track.get("trackViewUrl")

        answer = f"🎵 {title}\n👤 {artist}"

        if preview:
            answer += f"\n▶️ 30 soniyalik namuna: {preview}"
        if link:
            answer += f"\n🔗 {link}"

        await message.answer(answer)

except Exception:
    await message.answer("Xatolik yuz berdi. Keyinroq urinib ko‘ring.")
async def main():
await dp.start_polling(bot)

if name == "main":
asyncio.run(main())
