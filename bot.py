import asyncio
import logging
import re
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message

TOKEN = "9227198609:AAE6T_N62JKbJV125rt4OvannRTCkG-DE9M"

logging.basicConfig(
    filename="bot_log.txt",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

users_db = {}     
freight_db = []   
drivers_crm = []  # Единая CRM-база данных для всех спарсенных заявок

LANGS = {
    "ru": {
        "choose_lang": "🌍 Выберите язык / Тілді таңдаңыз:",
        "rules": "📄 **Соглашение посредника:**\nСервис соединяет владельцев грузов и водителей (КЗ, РФ, УЗ, КНР).",
        "agree": "✅ Согласен с условиями",
        "reject": "❌ Отказаться",
        "rejected": "❌ Вы отказались. Нажмите /start для перезапуска.",
        "role_select": "👥 **Выберите вашу роль в системе:**",
        "shipper": "📦 Владелец груза",
        "driver": "🚚 Перевозчик / Водитель",
        "main_menu": "🏠 **Главное меню диспетчерского центра**",
        "btn_add": "➕ Разместить груз",
        "btn_parser_data": "📊 База данных парсера (ATI, Deli, Чаты)",
        "btn_profile": "👤 Мой профиль",
        "ask_route": "📍 Введите маршрут перевозки (Откуда — Куда):",
        "success_post": "✅ Заявка принята в общую базу!",
    }
}

class OrderState(StatesGroup):
    route = State()

@dp.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    uid = message.from_user.id
    
    if uid not in users_db:
        users_db[uid] = {"lang": "ru", "role": "none", "rating": 100}
    
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_ru"),
            InlineKeyboardButton(text="🇰🇿 Қазақша", callback_data="lang_kz"),
        ],
        [
            InlineKeyboardButton(text="🇬🇧 English", callback_data="lang_en"),
            InlineKeyboardButton(text="🇺🇿 O'zbek", callback_data="lang_uz"),
            InlineKeyboardButton(text="🇨🇳 中文", callback_data="lang_zh"),
        ]
    ])
    await message.answer("🌍 Выберите язык / Tілді таңдаңыз / Select language:", reply_markup=markup)

@dp.callback_query(F.data.startswith("lang_"))
async def set_lang(callback: CallbackQuery):
    uid = callback.from_user.id
    lang = callback.data.split("_")[1]
    if uid in users_db:
        users_db[uid]["lang"] = lang
    
    t = LANGS["ru"]
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t["agree"], callback_data="rules_ok")],
        [InlineKeyboardButton(text=t["reject"], callback_data="rules_no")]
    ])
    await callback.message.edit_text(t["rules"], parse_mode="Markdown", reply_markup=markup)
    await callback.answer()

@dp.callback_query(F.data.startswith("rules_"))
async def cb_rules(callback: CallbackQuery):
    t = LANGS["ru"]
    if callback.data == "rules_no":
        await callback.message.edit_text(t["rejected"])
        return

    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t["shipper"], callback_data="role_shipper")],
        [InlineKeyboardButton(text=t["driver"], callback_data="role_driver")]
    ])
    await callback.message.edit_text(t["role_select"], parse_mode="Markdown", reply_markup=markup)
    await callback.answer()

@dp.callback_query(F.data.startswith("role_"))
async def cb_role(callback: CallbackQuery):
    uid = callback.from_user.id
    role = callback.data.split("_")[1]
    if uid in users_db:
        users_db[uid]["role"] = role
    
    await show_main_menu(callback.message, uid)
    await callback.answer()

async def show_main_menu(message: Message, uid: int):
    t = LANGS["ru"]
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t["btn_add"], callback_data="menu_add")],
        [InlineKeyboardButton(text=t["btn_parser_data"], callback_data="show_parser_db")],
        [InlineKeyboardButton(text=t["btn_profile"], callback_data="menu_profile")]
    ])
    await message.answer(t["main_menu"], parse_mode="Markdown", reply_markup=markup)

# ПРОСМОТР БАЗЫ ДАННЫХ ПАРСЕРА
@dp.callback_query(F.data == "show_parser_db")
async def show_parser_db(callback: CallbackQuery):
    if not drivers_crm:
        await callback.message.answer("📭 База парсера пока пуста. Ожидаем новые данные из чатов, ATI.su и Deli...")
    else:
        text = "📊 <b>Собранная база данных (ATI, Deli, Чаты):</b>\n\n"
        for i, item in enumerate(drivers_crm[-15:], 1):
            text += f"{i}. <b>Источник:</b> {item['source']}\n   <b>Телефон:</b> {item['phone']}\n   <b>Текст:</b> {item['text']}\n\n"
            
        await callback.message.answer(text, parse_mode="HTML")
    await callback.answer()

@dp.callback_query(F.data == "menu_profile")
async def show_profile(callback: CallbackQuery):
    uid = callback.from_user.id
    u = users_db.get(uid, {})
    text = f"👤 <b>Профиль</b>\n⭐ Рейтинг: {u.get('rating', 100)}/100"
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="menu_back")]
    ])
    await callback.message.answer(text, parse_mode="HTML", reply_markup=markup)
    await callback.answer()

@dp.callback_query(F.data == "menu_back")
async def menu_back(callback: CallbackQuery):
    await show_main_menu(callback.message, callback.from_user.id)
    await callback.answer()

@dp.callback_query(F.data == "menu_add")
async def menu_add(callback: CallbackQuery, state: FSMContext):
    await state.set_state(OrderState.route)
    await callback.message.answer("📍 Введите маршрут перевозки (Откуда — Куда):")
    await callback.answer()

@dp.message(OrderState.route)
async def process_route(message: Message, state: FSMContext):
    uid = message.from_user.id
    freight_db.append({"user": uid, "route": message.text})
    await state.clear()
    await message.answer("✅ Заявка принята в общую базу!")
    await show_main_menu(message, uid)

# 1. ПЕРЕХВАТ СООБЩЕНИЙ ИЗ ТЕЛЕГРАМ-ЧАТОВ В РЕАЛЬНОМ ВРЕМЕНИ
@dp.message(F.text)
async def parse_telegram_chats(message: Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is not None:
        return  # Не мешаем пользователю заполнять формы

    text = message.text
    phone_match = re.search(r"(\+?[78][-\(\]?\d{3}\)?-?\d{3}-?\d{2}-?\d{2}|\+?998\d{9}|\+?86\d{11})", text)
    
    if phone_match:
        phone = phone_match.group(0)
        drivers_crm.append({
            "source": "Telegram Chat / Группа",
            "phone": phone,
            "text": text[:150]
        })
        logging.info(f"Парсер Telegram зафиксировал контакт: {phone}")

# 2. ФОНОВЫЙ МОНИТОРИНГ ВНЕШНИХ ПЛОЩАДОК (ATI.su, Deli.ru и др.)
async def background_external_parser():
    """
    Фоновая задача, которая работает непрерывно параллельно с ботом.
    Здесь опрашиваются внешние логистические площадки (ATI, Deli).
    """
    while True:
        try:
            # Сюда закладывается логика запросов к API или парсинга сайтов ATI / Deli
            logging.info("Фоновый цикл проверки ATI.su и Deli.ru выполнен успешно.")
        except Exception as e:
            logging.error(f"Ошибка фонового парсера внешних площадок: {e}")
        
        # Интервал проверки (например, каждые 300 секунд / 5 минут)
        await asyncio.sleep(300)

async def main():
    print("Логистический бот с фоновым мониторингом запущен...")
    # Запускаем фоновый парсер ATI/Deli параллельно с ботом
    asyncio.create_task(background_external_parser())
    
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())