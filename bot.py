import telebot
from telebot import types

TOKEN = "9227198609:AAE6T_N62JKbJV125rt4OvannRTCkG-DE9M"
bot = telebot.TeleBot(TOKEN)

users = {}

TEXTS = {
    'ru': {
        'choose_lang': "🌍 Выберите язык / Тілді таңдаңыз:",
        'rules': "📄 **Соглашение посредника:**\n\nСервис соединяет владельцев грузов и водителей/перевозчиков (РК, РФ, РУЗ, КНР). Все расчеты и условия фиксируются через диспетчера.",
        'agree': "✅ Согласен с условиями",
        'reject': "❌ Отказаться",
        'rejected': "❌ Вы отказались. Для перезапуска нажмите /start",
        'role_select': "👥 **Выберите вашу роль в системе:**",
        'shipper': "📦 Владелец груза (Отправитель)",
        'driver': "🚚 Перевозчик / Водитель (Газелист/Фурист)",
        'main_menu': "🏠 **Главное меню посредника**",
        'btn_add': "➕ Разместить груз",
        'btn_search': "🔍 Найти груз / Маршруты",
        'btn_my': "📋 Мои заявки",
        'btn_contact': "📞 Связаться с диспетчером",
        'route_choose': "📍 Выберите направление перевозки:",
        'ask_desc': "📝 Опишите ваш груз (Откуда, куда, вес/объем, тип машины и желаемая ставка):",
        'success_post': "✅ Заявка успешно принята! Диспетчер свяжется с вами для подтверждения.",
        'no_loads': "📭 На данный момент свободных грузов по этому направлению нет.",
        'back': "⬅️ Назад в меню"
    },
    'kz': {
        'choose_lang': "🌍 Тілді таңдаңыз / Выберите язык:",
        'rules': "📄 **Делдалдық келісім:**\n\nСервис жүк иелері мен тасымалдаушыларды байланыстырады (ҚР, РФ, ӨЗБ, ҚХР). Барлық шарттар диспетчер арқылы бекітіледі.",
        'agree': "✅ Шарттармен келісемін",
        'reject': "❌ Бас тарту",
        'rejected': "❌ Сіз бас тарттыңыз. Қайта бастау үшін /start басыңыз",
        'role_select': "👥 **Жүйедегі рөліңізді таңдаңыз:**",
        'shipper': "📦 Жүк иесі (Тапсырыс беруші)",
        'driver': "🚚 Тасымалдаушы / Жүргізуші",
        'main_menu': "🏠 **Делдалдың басты мәзірі**",
        'btn_add': "➕ Жүкті орналастыру",
        'btn_search': "🔍 Жүк іздеу / Бағыттар",
        'btn_my': "📋 Менің тапсырыстарым",
        'btn_contact': "📞 Диспетчермен хабарласу",
        'route_choose': "📍 Тасымалдау бағытын таңдаңыз:",
        'ask_desc': "📝 Жүкті сипаттаңыз (Қайдан, қайда, салмағы/көлемі, көлік түрі және бағасы):",
        'success_post': "✅ Тапсырыс қабылданды! Диспетчер жақын арада хабарласады.",
        'no_loads': "📭 Бұл бағытта әзірге бос жүктер жоқ.",
        'back': "⬅️ Мәзірге оралу"
    },
    'en': {
        'choose_lang': "🌍 Select language:",
        'rules': "📄 **Intermediary Agreement:**\n\nService connects cargo owners and carriers (KZ, RU, UZ, CN). All terms are handled via dispatcher.",
        'agree': "✅ Agree",
        'reject': "❌ Decline",
        'rejected': "❌ You declined. Press /start to restart.",
        'role_select': "👥 **Select your role:**",
        'shipper': "📦 Cargo Owner (Shipper)",
        'driver': "🚚 Carrier / Driver",
        'main_menu': "🏠 **Main Intermediary Menu**",
        'btn_add': "➕ Post Cargo",
        'btn_search': "🔍 Search Cargoes / Routes",
        'btn_my': "📋 My Orders",
        'btn_contact': "📞 Contact Dispatcher",
        'route_choose': "📍 Select transport route:",
        'ask_desc': "📝 Enter cargo details (From, To, Weight/Volume, Truck type, Target rate):",
        'success_post': "✅ Cargo posted successfully! Dispatcher will contact you soon.",
        'no_loads': "📭 No active cargoes available for this route.",
        'back': "⬅️ Back to menu"
    },
    'uz': {
        'choose_lang': "🌍 Tilni tanlang:",
        'rules': "📄 **Vositachilik shartnomasi:**\n\nXizmat yuk egalari va tashuvchilarni bog'laydi (QZ, RU, UZ, CN). Barcha shartlar dispetcher orqali hal qilinadi.",
        'agree': "✅ Roziman",
        'reject': "❌ Rad etish",
        'rejected': "❌ Rad etdingiz. Qaytadan boshlash uchun /start bosing.",
        'role_select': "👥 **Rolingizni tanlang:**",
        'shipper': "📦 Yuk egasi",
        'driver': "🚚 Tashuvchi / Haydovchi",
        'main_menu': "🏠 **Asosiy menyu**",
        'btn_add': "➕ Yuk joylashtirish",
        'btn_search': "🔍 Yuklarni qidirish",
        'btn_my': "📋 Mening buyurtmalarim",
        'btn_contact': "📞 Dispetcher bilan bog'lanish",
        'route_choose': "📍 Yo'nalishni tanlang:",
        'ask_desc': "📝 Yuk tavsifini kiriting (Qayerdan, qayerga, vazni, mashina turi va narxi):",
        'success_post': "✅ Buyurtma qabul qilindi! Tez orada dispetcher bog'lanadi.",
        'no_loads': "📭 Hozircha bu yo'nalishda yuklar yo'q.",
        'back': "⬅️ Menюga qaytish"
    },
    'zh': {
        'choose_lang': "🌍 选择语言:",
        'rules': "📄 **中介服务协议：**\n\n本平台连接货主与承运人（哈萨克斯坦、俄罗斯、乌兹别克斯坦、中国）。所有订单由调度员跟进。",
        'agree': "✅ 同意条款",
        'reject': "❌ 拒绝",
        'rejected': "❌ 您已拒绝。请按 /start 重新开始。",
        'role_select': "👥 **选择您的身份：**",
        'shipper': "📦 货主",
        'driver': "🚚 承运人 / 司机",
        'main_menu': "🏠 **主菜单**",
        'btn_add': "➕ 发布货物",
        'btn_search': "🔍 查找货源 / 路线",
        'btn_my': "📋 我的订单",
        'btn_contact': "📞 联系调度员",
        'route_choose': "📍 选择运输路线：",
        'ask_desc': "📝 请输入货物详情（起止地、重量/体积、车型及期望运费）：",
        'success_post': "✅ 货源已成功发布！调度员将尽快与您联系。",
        'no_loads': "📭 该路线目前暂无可用货源。",
        'back': "⬅️ 返回主菜单"
    }
}

@bot.message_handler(commands=['start'])
def cmd_start(message):
    cid = message.chat.id
    users[cid] = {'lang': 'ru', 'role': None, 'state': None}
    
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru"),
        types.InlineKeyboardButton("🇰🇿 Қазақша", callback_data="lang_kz"),
        types.InlineKeyboardButton("🇬🇧 English", callback_data="lang_en"),
        types.InlineKeyboardButton("🇺🇿 O'zbek", callback_data="lang_uz"),
        types.InlineKeyboardButton("🇨🇳 中文", callback_data="lang_zh")
    )
    bot.send_message(cid, TEXTS['ru']['choose_lang'], reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('lang_'))
def cb_lang(call):
    cid = call.message.chat.id
    lang = call.data.split('_')[1]
    if cid not in users:
        users[cid] = {}
    users[cid]['lang'] = lang
    t = TEXTS[lang]

    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton(t['agree'], callback_data="rules_ok"),
        types.InlineKeyboardButton(t['reject'], callback_data="rules_no")
    )
    bot.edit_message_text(t['rules'], cid, call.message.message_id, parse_mode='Markdown', reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('rules_'))
def cb_rules(call):
    cid = call.message.chat.id
    lang = users.get(cid, {}).get('lang', 'ru')
    t = TEXTS[lang]

    if call.data == 'rules_no':
        bot.edit_message_text(t['rejected'], cid, call.message.message_id)
        return

    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton(t['shipper'], callback_data="role_shipper"),
        types.InlineKeyboardButton(t['driver'], callback_data="role_driver")
    )
    bot.edit_message_text(t['role_select'], cid, call.message.message_id, parse_mode='Markdown', reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('role_'))
def cb_role(call):
    cid = call.message.chat.id
    role = call.data.split('_')[1]
    if cid not in users:
        users[cid] = {'lang': 'ru'}
    users[cid]['role'] = role
    lang = users[cid]['lang']
    
    send_main_menu(cid, lang, call.message.message_id)

def send_main_menu(cid, lang, msg_id=None):
    t = TEXTS[lang]
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton(t['btn_add'], callback_data="menu_add"),
        types.InlineKeyboardButton(t['btn_search'], callback_data="menu_search"),
        types.InlineKeyboardButton(t['btn_my'], callback_data="menu_my"),
        types.InlineKeyboardButton(t['btn_contact'], callback_data="menu_contact")
    )
    if msg_id:
        bot.edit_message_text(t['main_menu'], cid, msg_id, parse_mode='Markdown', reply_markup=markup)
    else:
        bot.send_message(cid, t['main_menu'], parse_mode='Markdown', reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('menu_'))
def cb_menu(call):
    cid = call.message.chat.id
    action = call.data.split('_')[1]
    lang = users.get(cid, {}).get('lang', 'ru')
    t = TEXTS[lang]

    if action == 'add':
        users[cid]['state'] = 'waiting_cargo'
        bot.send_message(cid, t['ask_desc'])
    elif action == 'search':
        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(
            types.InlineKeyboardButton("🇰🇿 Казахстан", callback_data="reg_kz"),
            types.InlineKeyboardButton("🇷🇺 Россия", callback_data="reg_ru"),
            types.InlineKeyboardButton("🇺🇿 Узбекистан", callback_data="reg_uz"),
            types.InlineKeyboardButton("🇨🇳 Китай", callback_data="reg_cn"),
            types.InlineKeyboardButton(t['back'], callback_data="menu_back")
        )
        bot.edit_message_text(t['route_choose'], cid, call.message.message_id, reply_markup=markup)
    elif action == 'my':
        bot.answer_callback_query(call.id, "Список ваших заявок пуст")
        bot.send_message(cid, "📋 У вас пока нет активных заявок в системе.")
    elif action == 'contact':
        bot.send_message(cid, "📞 Контакты диспетчера-посредника:\nTelegram: @vsegruzy_admin\nТелефон / WhatsApp: +7 (700) 000-00-00")
    elif action == 'back':
        send_main_menu(cid, lang, call.message.message_id)

@bot.callback_query_handler(func=lambda call: call.data.startswith('reg_'))
def cb_region(call):
    cid = call.message.chat.id
    lang = users.get(cid, {}).get('lang', 'ru')
    t = TEXTS[lang]
    bot.answer_callback_query(call.id)
    bot.send_message(cid, t['no_loads'])

@bot.message_handler(func=lambda msg: users.get(msg.chat.id, {}).get('state') == 'waiting_cargo')
def text_cargo_handler(msg):
    cid = msg.chat.id
    lang = users.get(cid, {}).get('lang', 'ru')
    t = TEXTS[lang]
    
    users[cid]['state'] = None
    bot.send_message(cid, t['success_post'])
    send_main_menu(cid, lang)

if __name__ == '__main__':
    print("Запуск логистического бота...")
    try:
        bot.remove_webhook()
    except:
        pass
    print("Бот успешно запущен и готов принимать сообщения.")
    bot.infinity_polling(skip_pending=True)