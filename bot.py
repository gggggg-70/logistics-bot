import asyncio
import logging
import re
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message

# 1. ТОКЕН И ЛОГИРОВАНИЕ
TOKEN = "9227198609:AAE6T_N62JKbJV125rt4OvannRTCkG-DE9M"

logging.basicConfig(
    filename="bot_log.txt",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# 2. БАЗЫ ДАННЫХ В ПАМЯТИ
users_db = {}     # Профили пользователей, языки, роли, рейтинги
freight_db = []   # Реестр заявок на грузы
drivers_crm = {}  # CRM водителей и парсинга

# 3. ПОЛНЫЕ СЛОВАРИ НА 5 ЯЗЫКОВ
LANGS = {
    "ru": {
        "choose_lang": "🌍 Выберите язык / Тілді таңдаңыз:",
        "rules": "📄 **Соглашение посредника:**\nСервис соединяет владельцев грузов и водителей (КЗ, РФ, УЗ, КНР). Все расчеты через диспетчера.",
        "agree": "✅ Согласен с условиями",
        "reject": "❌ Отказаться",
        "rejected": "❌ Вы отказались. Нажмите /start для перезапуска.",
        "role_select": "👥 **Выберите вашу роль в системе:**",
        "shipper": "📦 Владелец груза (Отправитель)",
        "driver": "🚚 Перевозчик / Водитель",
        "main_menu": "🏠 **Главное меню диспетчерского центра**",
        "btn_add": "➕ Разместить груз",
        "btn_search": "🔍 Найти грузы / Маршруты",
        "btn_profile": "👤 Мой профиль",
        "ask_route": "📍 Введите маршрут перевозки (Откуда — Куда):",
        "success_post": "✅ Заявка принята в общую базу и отправлена в рассылку!",
    },
    "kz": {
        "choose_lang": "🌍 Тілді таңдаңыз / Выберите язык:",
        "rules": "📄 **Делдалдық келісім:**\nСервис жүк иелері мен тасымалдаушыларды байланыстырады (ҚР, РФ, ӨЗБ, ҚХР). Барлық есеп айырысу диспетчер арқылы.",
        "agree": "✅ Шарттармен келісемін",
        "reject": "❌ Бас тарту",
        "rejected": "❌ Сіз бас тарттыңыз. Қайта бастау үшін /start басыңыз.",
        "role_select": "👥 **Жүйедегі рөліңізді таңдаңыз:**",
        "shipper": "📦 Жүк иесі (Тапсырыс беруші)",
        "driver": "🚚 Тасымалдаушы / Жүргізуші",
        "main_menu": "🏠 **Диспетчерлік орталықтың басты мәзірі**",
        "btn_add": "➕ Жүкті орналастыру",
        "btn_search": "🔍 Жүк іздеу / Бағыттар",
        "btn_profile": "👤 Менің профилім",
        "ask_route": "📍 Тасымалдау бағытын енгізіңіз (Қайдан — Қайда):",
        "success_post": "✅ Тапсырыс базаға қабылданды және таратуға жіберілді!",
    },
    "en": {
        "choose_lang": "🌍 Select language:",
        "rules": "📄 **Intermediary Agreement:**\nService connects cargo owners and carriers (KZ, RU, UZ, CN). All settlements via dispatcher.",
        "agree": "✅ Agree",
        "reject": "❌ Decline",
        'rejected': "❌ You declined. Press /start to restart.",
        "role_select": "👥 **Select your role:**",
        "shipper": "📦 Cargo Owner (Shipper)",
        "driver": "🚚 Carrier / Driver",
        "main_menu": "🏠 **Main Dispatch Center Menu**",
        "btn_add": "➕ Post Cargo",
        "btn_search": "🔍 Search Cargoes / Routes",
        "btn_profile": "👤 My Profile",
        "ask_route": "📝 Enter transport route (From — To):",
        "success_post": "✅ Cargo posted successfully and sent to dispatch!",
    },
    "uz": {
        "choose_lang": "🌍 Tilni tanlang:",
        "rules": "📄 **Vositachilik shartnomasi:**\nXizmat yuk egalari va tashuvchilarni bog'laydi (QZ, RU, UZ, CN). Barcha hisob-kitoblar dispetcher orqali.",
        "agree": "✅ Roziman",
        "reject": "❌ Rad etish",
        "rejected": "❌ Rad etdingiz. Qaytadan boshlash uchun /start bosing.",
        "role_select": "👥 **Rolingizni tanlang:**",
        "shipper": "📦 Yuk egasi",
        "driver": "🚚 Tashuvchi / Haydovchi",
        "main_menu": "🏠 **Asosiy dispetcherlik menyusi**",
        "btn_add": "➕ Yuk joylashtirish",
        "btn_search": "🔍 Yuklarni qidirish",
        "btn_profile": "👤 Mening profilim",
        "ask_route": "📝 Yo'nalishni kiriting (Qayerdan — Qayerga):",
        "success_post": "✅ Buyurtma bazaga qo'shildi va tarqatishga yuborildi!",
    },
    "cn": {
        "choose_lang": "🌍 选择语言:",
        "rules": "📄 **中介服务协议：**\n本平台连接货主与承运人（哈萨克斯坦、俄罗斯、乌兹别克斯坦、中国）。所有结算通过调度员进行。",
        "agree": "✅ 同意条款",
        "reject": "❌ 拒绝",
        "rejected": "❌ 您已拒绝。请按 /start 重新开始。",
        "role_select": "👥 **选择您的身份：**",
        "shipper": "📦 货主",
        "driver": "🚚 承运人 / 司机",
        "main_menu": "🏠 **调度中心主菜单**",
        "btn_add": "➕ 发布货物",
        "btn_search": "🔍 查找货源 / 路线",
        "btn_profile": "👤 我的资料",
        "ask_route": "📝 请输入运输路线（起止地）：",
        "success_post": "✅ 货源已成功发布并进入推送队列！",
    },
}

def get_text(user_id: int, key: str) -> str:
    lang = users_db.get(user_id, {}).get("lang", "ru")
    return LANGS.get(lang, LANGS["ru"]).get(key, key)

# 4. FSM СОСТОЯНИЯ ДЛЯ ПОДАЧИ ГРУЗА
class OrderState(StatesGroup):
    route = State()

# 5. СТАРТ И ВЫБОР ЯЗЫКА
@dp.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    uid = message.from_user.id
    
    if uid not in users_db:
        users_db[uid] = {
            "lang": "ru", 
            "role": "none", 
            "rating": 100, 
            "is_paid_restored": False,
            "username": message.from_user.username or "нет"
        }
    
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
    
    t = LANGS.get(lang, LANGS["ru"])
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t["agree"], callback_data="rules_ok")],
        [InlineKeyboardButton(text=t["reject"], callback_data="rules_no")]
    ])
    await callback.message.edit_text(t["rules"], parse_mode="Markdown", reply_markup=markup)
    await callback.answer()

@dp.callback_query(F.data.startswith("rules_"))
async def cb_rules(callback: CallbackQuery):
    uid = callback.from_user.id
    lang = users_db.get(uid, {}).get("lang", "ru")
    t = LANGS.get(lang, LANGS["ru"])

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
    lang = users_db.get(uid, {}).get("lang", "ru")
    t = LANGS.get(lang, LANGS["ru"])
    
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t["btn_add"], callback_data="menu_add")],
        [InlineKeyboardButton(text=t["btn_profile"], callback_data="menu_profile")]
    ])
    await message.answer(t["main_menu"], parse_mode="Markdown", reply_markup=markup)

# 6. КАБИНЕТ И ПЛАТНОЕ ВОССТАНОВЛЕНИЕ РЕЙТИНГА
@dp.callback_query(F.data == "menu_profile")
async def show_profile(callback: CallbackQuery):
    uid = callback.from_user.id
    u = users_db.get(uid, {})
    rating = u.get("rating", 100)
    badge = "\n⚠️ Статус: Рейтинг восстановлен за плату" if u.get("is_paid_restored") else ""
    
    text = f"👤 **Профиль**\n⭐ Рейтинг: {rating}/100{badge}"
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💳 Восстановить рейтинг (Экв.)", callback_data="pay_restore")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="menu_back")]
    ])
    await callback.message.answer(text, parse_mode="Markdown", reply_markup=markup)
    await callback.answer()

@dp.callback_query(F.data == "pay_restore")
async def pay_restore(callback: CallbackQuery):
    uid = callback.from_user.id
    users_db[uid]["rating"] = 100
    users_db[uid]["is_paid_restored"] = True
    await callback.message.answer("✅ Оплата прошла успешно! Ваш рейтинг восстановлен до 100.")
    await show_main_menu(callback.message, uid)
    await callback.answer()

@dp.callback_query(F.data == "menu_back")
async def menu_back(callback: CallbackQuery):
    await show_main_menu(callback.message, callback.from_user.id)
    await callback.answer()

# 7. ПОДАЧА ГРУЗА
@dp.callback_query(F.data == "menu_add")
async def menu_add(callback: CallbackQuery, state: FSMContext):
    uid = callback.from_user.id
    lang = users_db.get(uid, {}).get("lang", "ru")
    t = LANGS.get(lang, LANGS["ru"])
    
    await state.set_state(OrderState.route)
    await callback.message.answer(t["ask_route"])
    await callback.answer()

@dp.message(OrderState.route)
async def process_route(message: Message, state: FSMContext):
    uid = message.from_user.id
    lang = users_db.get(uid, {}).get("lang", "ru")
    t = LANGS.get(lang, LANGS["ru"])
    
    freight_db.append({"user": uid, "route": message.text})
    await state.clear()
    await message.answer(t["success_post"])
    await show_main_menu(message, uid)

# 8. ПАРСИНГ ТЕЛЕГРАМ-ЧАТОВ И ВНЕШНИХ ИСТОЧНИКОВ
@dp.message(F.text & ~F.command)
async def parse_external_chats(message: Message):
    text = message.text
    uid = message.from_user.id
    
    # Автоматический перехват номеров телефонов из чатов (КЗ, РУЗ, КНР, РФ)
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
    print("Чистый запуск логистического бота...")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())