import os
import aiohttp
import asyncio
from dotenv import load_dotenv
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from telegram import Bot, InputMediaPhoto

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
API_URL = os.getenv("API_URL")
AFFILIATE_TAG = os.getenv("AFFILIATE_TAG")

bot = Bot(token=TELEGRAM_BOT_TOKEN)

# Function to fetch product data from API
async def fetch_products():
    async with aiohttp.ClientSession() as session:
        async with session.get(API_URL) as resp:
            if resp.status == 200:
                return await resp.json()
            else:
                print("Failed to fetch product data")
                return []

# Function to post products to Telegram
async def post_to_telegram():
    print("🔁 Checking for new products...")
    products = await fetch_products()
    
    for product in products[:5]:  # Limit to top 5 each run
        title = product.get("title")
        price = product.get("price")
        image = product.get("image")
        link = product.get("url")

        # Modify the link to include affiliate tag
        if "amazon" in link:
            if "?tag=" not in link:
                if "?" in link:
                    link += f"&tag={AFFILIATE_TAG}"
                else:
                    link += f"?tag={AFFILIATE_TAG}"

        message = f"🛒 *{title}*\n💸 Price: {price}\n👉 [Buy Now]({link})"
        try:
            await bot.send_photo(
                chat_id=CHAT_ID,
                photo=image,
                caption=message,
                parse_mode="Markdown"
            )
        except Exception as e:
            print(f"❌ Failed to send product: {e}")

# Main loop with scheduler
async def main():
    scheduler = AsyncIOScheduler()
    scheduler.add_job(post_to_telegram, "interval", minutes=60)  # every hour
    scheduler.start()

    print("✅ Bot is running...")
    while True:
        await asyncio.sleep(10)

if __name__ == "__main__":
    asyncio.run(main())
