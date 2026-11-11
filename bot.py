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
drivers_crm = {}  

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
        "btn_parser_data": "📊 База данных парсера (CRM)",
        "btn_profile": "👤 Мой профиль",
        "ask_route": "📍 Введите маршрут перевозки (Откуда — Куда):",
        "success_post": "✅ Заявка принята в общую базу!",
    }
}

def get_text(user_id: int, key: str) -> str:
    lang = users_db.get(user_id, {}).get("lang", "ru")
    return LANGS.get(lang, LANGS["ru"]).get(key, key)

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
    uid = callback.from_user.id
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

@dp.callback_query(F.data == "show_parser_db")
async def show_parser_db(callback: CallbackQuery):
    uid = callback.from_user.id
    if not drivers_crm:
        await callback.message.answer("📭 База парсера пока пуста. Никаких объявлений или телефонов в чатах еще не перехвачено.")
    else:
        text = "📊 <b>Собранная база данных (Парсер / CRM):</b>\n\n"
        for i, (usr_id, data) in enumerate(drivers_crm.items(), 1):
            text += f"{i}. <b>Телефон:</b> {data['phone']}\n   <b>User:</b> @{data['username']}\n   <b>Текст:</b> {data['text']}\n\n"
        
        if len(text) > 4000:
            text = text[:4000] + "\n...(список слишком длинный)"
            
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

@dp.message(F.text & ~F.command)
async def parse_external_chats(message: Message):
    text = message.text
    uid = message.from_user.id
    
    phone_match = re.search(r"(\+?[78][-\(\]?\d{3}\)?-?\d{3}-?\d{2}-?\d{2}|\+?998\d{9}|\+?86\d{11})", text)
    if phone_match:
        phone = phone_match.group(0)
        drivers_crm[uid] = {
            "phone": phone,
            "username": message.from_user.username or "нет",
            "text": text[:100]
        }
        logging.info(f"Парсер зафиксировал контакт: {phone} от пользователя {uid}")

async def main():
    print("Бот с активным просмотром базы парсинга запущен...")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())