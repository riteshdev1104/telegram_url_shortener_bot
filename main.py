from fastapi import FastAPI, Request
from aiogram import Bot, Dispatcher, types
from aiogram.utils.executor import start_webhook
import aiohttp
import os

TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_HOST = "https://your-render-url.onrender.com"
WEBHOOK_PATH = f"/webhook/{{TOKEN}}"
WEBHOOK_URL = f"{{WEBHOOK_HOST}}{{WEBHOOK_PATH}}"

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)
app = FastAPI()

async def shorten_url(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://is.gd/create.php?format=simple&url={{url}}") as resp:
            return await resp.text()

@dp.message_handler()
async def handle_message(message: types.Message):
    if message.text.startswith("http"):
        short_url = await shorten_url(message.text)
        await message.reply(f"Shortened URL: {{short_url}}")
    else:
        await message.reply("Send a valid URL starting with http.")

@app.post(WEBHOOK_PATH)
async def webhook(request: Request):
    update = types.Update(**await request.json())
    await dp.process_update(update)
    return {{"ok": True}}

@app.on_event("startup")
async def on_startup():
    await bot.set_webhook(WEBHOOK_URL)

@app.on_event("shutdown")
async def on_shutdown():
    await bot.delete_webhook()
