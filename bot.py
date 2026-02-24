import logging
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import ParseMode
from aiogram.utils import executor
from config.settings import TELEGRAM_BOT_TOKEN, ADMIN_ID
import importlib.util
import sys

# Manually load the parser module first to avoid conflict
target_file = "parser.py"
spec = importlib.util.spec_from_file_location("parser", target_file)
parser = importlib.util.module_from_spec(spec)
spec.loader.exec_module(parser)

# Manually load the database module
db_file = "database.py"
spec = importlib.util.spec_from_file_location("database", db_file)
database = importlib.util.module_from_spec(spec)
spec.loader.exec_module(database)

# Extract required functions
init_db = database.init_db
save_user = database.save_user
get_latest_tours = database.get_latest_tours
get_existing_tour_ids = database.get_existing_tour_ids
get_new_tours = parser.get_new_tours

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("C:/Users/NISI/Desktop/PEP/tour_bot/logs/bot.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Initialize bot and dispatcher
bot = Bot(token=TELEGRAM_BOT_TOKEN)
dp = Dispatcher(bot)

def format_tour_message(tour: dict) -> str:
    """
    Format tour data into readable message
    """
    return f"""
⛱ <b>{tour['hotel_name']}</b> ({tour['hotel_rating']}★)

📌 <b>{tour['title']}</b>
📅 Вылет: {tour['departure_date']}
🌙 Ночей: {tour['nights']}
🍽 Питание: {tour['meal_type']}
✈️ Перелет: {tour['flight_info']}

💰 <b>Цена: {tour['price']:,} ₽</b>

👉 {tour['url']}
""".strip()

@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    """
    Handle /start and /help commands
    """
    user_data = {
        'id': message.from_user.id,
        'username': message.from_user.username,
        'first_name': message.from_user.first_name,
        'last_name': message.from_user.last_name
    }
    save_user(user_data)
    
    welcome_text = """
👋 Привет! Я бот для поиска туров в Паттайю из Москвы.

Доступные команды:
/search - Найти туры в Паттайю
/latest - Посмотреть последние найденные туры
/help - Показать это сообщение

Я ищу только прямые рейсы и показываю лучшие предложения!"""
    
    await message.answer(welcome_text, parse_mode=ParseMode.HTML)

@dp.message_handler(commands=['search'])
async def search_tours(message: types.Message):
    """
    Search for tours and send results
    """
    await message.answer("🔍 Ищу туры в Паттайю из Москвы...")
    
    try:
        # Get existing tour IDs
        existing_ids = get_existing_tour_ids()
        
        # Parse new tours
        new_tours = get_new_tours(existing_ids)
        
        if new_tours:
            # Save new tours to database
            from database import save_tours
            save_tours(new_tours)
            
            # Send new tours
            for tour in new_tours[:5]:  # Send top 5 new tours
                await message.answer(
                    format_tour_message(tour.__dict__),
                    parse_mode=ParseMode.HTML,
                    disable_web_page_preview=True
                )
            
            await message.answer(f"✅ Найдено {len(new_tours)} новых туров!")
        else:
            await message.answer("❌ Нет новых туров в Паттайю. Попробуйте позже.")
            
    except Exception as e:
        logger.error(f"Error searching tours: {e}")
        await message.answer("❌ Произошла ошибка при поиске туров. Попробуйте позже.")

@dp.message_handler(commands=['latest'])
async def show_latest_tours(message: types.Message):
    """
    Show latest tours from database
    """
    await message.answer("⏳ Получаю последние предложения...")
    
    try:
        tours = get_latest_tours(limit=5)
        
        if tours:
            for tour in tours:
                await message.answer(
                    format_tour_message(dict(tour)),
                    parse_mode=ParseMode.HTML,
                    disable_web_page_preview=True
                )
            await message.answer(f"📋 Показано {len(tours)} последних предложений.")
        else:
            await message.answer("❌ Нет сохраненных туров. Используйте /search чтобы найти первые предложения.")
            
    except Exception as e:
        logger.error(f"Error showing latest tours: {e}")
        await message.answer("❌ Произошла ошибка при получении туров.")

async def notify_new_tours():
    """
    Periodically check for new tours and notify admin
    """
    while True:
        try:
            # Get existing tour IDs
            existing_ids = get_existing_tour_ids()
            
            # Parse new tours
            new_tours = get_new_tours(existing_ids)
            
            if new_tours:
                # Save new tours to database
                from database import save_tours
                save_tours(new_tours)
                
                # Notify admin
                for tour in new_tours[:3]:  # Notify about top 3 new tours
                    await bot.send_message(
                        ADMIN_ID,
                        f"🎉 Найден новый тур в Паттайю!\n\n{format_tour_message(tour.__dict__)}",
                        parse_mode=ParseMode.HTML,
                        disable_web_page_preview=True
                    )
                
                logger.info(f"Notified admin about {len(new_tours)} new tours")
            
        except Exception as e:
            logger.error(f"Error in periodic check: {e}")
        
        # Wait 1 hour before next check
        await asyncio.sleep(3600)

if __name__ == '__main__':
    # Initialize database
    init_db()
    
    # Start bot
    executor.start_polling(dp, skip_updates=True)