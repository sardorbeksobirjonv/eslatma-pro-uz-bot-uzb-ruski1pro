from telegram import (
    Update,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    KeyboardButton,
)
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import asyncio

# ================= TOKEN =================
TOKEN = "8528647202:AAHQOrW3p8M0uLTTTDF_M2LKtSqVAs92Mvw"

# ================= STATES =================
(
    TIL,
    KONTAKT,
    MINTQA,
    TUR,
    TARGET_ID,
    MATN,         
    VAQT,         
    QAYTA,
    MENU,
    TAHRIR_ID,
    TAHRIR_TURI,
    TAHRIR_KIRITISH,
) = range(12)

users = {}

# ================= LANGUAGES & TEXTS =================
TEXTS = {
    "O‘zbekcha": {
        "welcome": "👋 Assalomu alaykum!\nMen sizga kerakli vaqtda eslatmalar yuboruvchi botman.",
        "menu": "📌 Asosiy menyu",
        "new_rem": "➕ Yangi eslatma",
        "list": "📋 Ro‘yxat",
        "type_select": "🔔 Еслатма турини танланг\n👤 Шахсий — еслатма фақат сизга кўринади\n👥 Гуруҳ — еслатма гуруҳда ишлайди\n📢 Канал — еслатма каналга юборилади\n📘 Қўлланма — ботdan qanday foydalanishni bilish",
        "personal": "👤 Shaxsiy",
        "group": "👥 Guruh",
        "channel": "📢 Kanal",
        "target_id": "🆔 Guruh/Kanal ID yoki @username kiriting\nMasalan:\n-1001234567890\n@my_channel",
        "time_format": "⏰ Eslatmaning vaqti\n📅 Sana va vaqtni quyidagi formatda kiriting:\nDD.MM.YYYY HH:MM\n📌 Misol: 25.01.2026 18:30",
        "input_text": "✏️ Eslatma matnini kiriting",
        "repeat": "🔁 Takrorlansinmi?",
        "saved": "✅ Eslatma saqlandi",
        "empty": "📭 Eslatmalar yo‘q",
        "edit_list": "✏️ Eslatmani tahrirlash uchun quyidagilardan birini tanlang:",
        "edit_type": "✏️ Nimani o‘zgartiramiz?",
        "edit_val": "Yangi qiymatni kiriting",
        "error_fmt": "❌ Format noto‘g‘ri",
        "error_region": "❌ Mintaqa topilmadi, qayta yozing",
        "region_ask": "🌍 Mintaqani yozing (masalan: Tashkent)",
        "btn_text": "Matn",
        "btn_time": "Vaqt",
        "btn_del": "O‘chirish"
    },
    "Русский": {
        "welcome": "👋 Здравствуйте!\nЯ бот, который будет присылать вам напоминания в нужное время.",
        "menu": "📌 Главное меню",
        "new_rem": "➕ Новое напоминание",
        "list": "📋 Список",
        "type_select": "🔔 Выберите тип напоминания\n👤 Личное — только для вас\n👥 Группа — напоминание в группе\n📢 Канал — напоминание в канал\n📘 Руководство — как пользоваться ботом",
        "personal": "👤 Личное",
        "group": "👥 Группа",
        "channel": "📢 Канал",
        "target_id": "🆔 Введите ID группы/канала или @username\nНапример:\n-1001234567890\n@my_channel",
        "time_format": "⏰ Время напоминания\n📅 Введите дату и время в формате:\nDD.MM.YYYY HH:MM\n📌 Пример: 25.01.2026 18:30",
        "input_text": "✏️ Введите текст напоминания",
        "repeat": "🔁 Повторять?",
        "saved": "✅ Напоминание сохранено",
        "empty": "📭 Напоминаний нет",
        "edit_list": "✏️ Выберите напоминание для редактирования:",
        "edit_type": "✏️ Что изменим?",
        "edit_val": "Введите новое значение",
        "error_fmt": "❌ Неверный формат",
        "error_region": "❌ Регион не найден, попробуйте еще раз",
        "region_ask": "🌍 Напишите регион (например: Moscow или Tashkent)",
        "btn_text": "Текст",
        "btn_time": "Время",
        "btn_del": "Удалить"
    }
}

ZONE_MAP = {
    "toshkent": "Asia/Tashkent", "tashkent": "Asia/Tashkent", "ташкент": "Asia/Tashkent",
    "moskva": "Europe/Moscow", "москва": "Europe/Moscow",
    "new york": "America/New_York", "ny": "America/New_York", "нью-йорк": "America/New_York",
    "istanbul": "Europe/Istanbul", "истамбул": "Europe/Istanbul",
    "tokyo": "Asia/Tokyo", "токио": "Asia/Tokyo",
    "berlin": "Europe/Berlin", "берлин": "Europe/Berlin",
    "london": "Europe/London", "лондон": "Europe/London",
    "paris": "Europe/Paris", "париж": "Europe/Paris",
    "dubai": "Asia/Dubai", "дубай": "Asia/Dubai",
}

REPEAT_MAPS = {
    "O‘zbekcha": {
        "Hech qachon": None, "Har kun": timedelta(days=1), "Har 2 hafta": timedelta(weeks=2),
        "Har hafta": timedelta(weeks=1), "Har oy": timedelta(days=30), "Choraklik (3 oy)": timedelta(days=90),
        "Har 6 oy": timedelta(days=180), "Har yil": timedelta(days=365)
    },
    "Русский": {
        "Никогда": None, "Каждый день": timedelta(days=1), "Каждые 2 недели": timedelta(weeks=2),
        "Каждую неделю": timedelta(weeks=1), "Каждый месяц": timedelta(days=30), "Квартально (3 мес)": timedelta(days=90),
        "Раз в 6 месяцев": timedelta(days=180), "Каждый год": timedelta(days=365)
    }
}

def parse_chat_id(text: str):
    text = text.strip()
    if text.startswith("@"): return text
    if text.startswith("https://t.me/"):
        username = text.split("/")[-1]
        return "@" + username if username else None
    try: return int(text)
    except: return None

# ================= handlers =================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    
    # AGAR FOYDALANUVCHI OLDIN RO'YXATDAN O'TGAN BO'LSA (TIL VA TZ BOR BO'LSA)
    if uid in users and "lang" in users[uid] and "tz" in users[uid]:
        # Conversation state'ni menyuga o'tkazamiz
        return await menu(update, context)

    # AKS HOLDA (BIRINCHI MARTA START BOSGANDA)
    users[uid] = {"reminders": [], "tz": None, "lang": None}
    
    await update.message.reply_text(
        "Tilni tanlang / Выберите язык:",
        reply_markup=ReplyKeyboardMarkup([["O‘zbekcha", "Русский"]], resize_keyboard=True)
    )
    return TIL

async def til(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    lang = update.message.text
    if lang not in ["O‘zbekcha", "Русский"]: return TIL
    users[uid]["lang"] = lang
    await update.message.reply_text(TEXTS[lang]["region_ask"], reply_markup=ReplyKeyboardRemove())
    return MINTQA

async def mintqa(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    lang = users[uid]["lang"]
    text = update.message.text.lower()
    if text in ZONE_MAP:
        users[uid]["tz"] = ZoneInfo(ZONE_MAP[text])
        return await menu(update, context)
    await update.message.reply_text(TEXTS[lang]["error_region"])
    return MINTQA

async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    lang = users[uid].get("lang", "O‘zbekcha")
    await update.message.reply_text(
        TEXTS[lang]["menu"],
        reply_markup=ReplyKeyboardMarkup([[TEXTS[lang]["new_rem"]], [TEXTS[lang]["list"]]], resize_keyboard=True)
    )
    return MENU

async def menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    lang = users[uid]["lang"]
    text = update.message.text
    if text == TEXTS[lang]["new_rem"]:
        await update.message.reply_text(
            TEXTS[lang]["type_select"],
            reply_markup=ReplyKeyboardMarkup([[TEXTS[lang]["personal"]], [TEXTS[lang]["group"]], [TEXTS[lang]["channel"]]], resize_keyboard=True)
        )
        return TUR
    elif text == TEXTS[lang]["list"]:
        if not users[uid]["reminders"]:
            await update.message.reply_text(TEXTS[lang]["empty"])
            return MENU
        buttons = [[f"{r['text']} | {r['time'].strftime('%d.%m.%Y %H:%M')}"] for r in users[uid]["reminders"]]
        await update.message.reply_text(TEXTS[lang]["edit_list"], reply_markup=ReplyKeyboardMarkup(buttons, resize_keyboard=True))
        return TAHRIR_ID
    return MENU

async def tur(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    lang = users[uid]["lang"]
    text = update.message.text
    if text == TEXTS[lang]["personal"]: users[uid]["current"] = {"type": "private"}
    elif text == TEXTS[lang]["group"]: users[uid]["current"] = {"type": "group"}
    elif text == TEXTS[lang]["channel"]: users[uid]["current"] = {"type": "channel"}
    else: return TUR

    if users[uid]["current"]["type"] in ["group", "channel"]:
        await update.message.reply_text(TEXTS[lang]["target_id"])
        return TARGET_ID
    
    await update.message.reply_text(TEXTS[lang]["input_text"])
    return MATN

async def target_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    lang = users[uid]["lang"]
    cid = parse_chat_id(update.message.text)
    if cid is None:
        await update.message.reply_text("ID error")
        return TARGET_ID
    users[uid]["current"]["target_id"] = cid
    await update.message.reply_text(TEXTS[lang]["input_text"])
    return MATN

async def matn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    lang = users[uid]["lang"]
    users[uid]["current"]["text"] = update.message.text
    await update.message.reply_text(TEXTS[lang]["time_format"])
    return VAQT

async def vaqt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    lang = users[uid]["lang"]
    try:
        dt = datetime.strptime(update.message.text, "%d.%m.%Y %H:%M")
        users[uid]["current"]["time"] = dt
        reps = list(REPEAT_MAPS[lang].keys())
        kb = [reps[i:i+3] for i in range(0, len(reps), 3)]
        await update.message.reply_text(TEXTS[lang]["repeat"], reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True))
        return QAYTA
    except:
        await update.message.reply_text(TEXTS[lang]["error_fmt"])
        return VAQT

async def qayta(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    lang = users[uid]["lang"]
    cur = users[uid]["current"]
    cur["repeat"] = REPEAT_MAPS[lang].get(update.message.text)
    cur["task"] = asyncio.create_task(schedule(uid, cur, context))
    users[uid]["reminders"].append(cur)
    users[uid].pop("current")
    await update.message.reply_text(TEXTS[lang]["saved"])
    return await menu(update, context)

async def schedule(uid, r, context):
    while True:
        if uid not in users: return
        tz = users[uid]["tz"]
        now = datetime.now(tz)
        target = r["time"].replace(tzinfo=tz)
        if target <= now:
            if not r["repeat"]: break
            target += r["repeat"]
        
        await asyncio.sleep(max(1, (target - now).total_seconds()))
        chat_id = uid if r["type"] == "private" else r["target_id"]
        try:
            await context.bot.send_message(chat_id=chat_id, text=f"⏰ Eslatma / Напоминание:\n\n{r['text']}")
        except: pass
        if not r["repeat"]: break
        r["time"] = target

async def tahrir_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    lang = users[uid]["lang"]
    for r in users[uid]["reminders"]:
        if r["text"] in update.message.text:
            users[uid]["edit"] = r
            break
    else: return await menu(update, context)
    kb = [[TEXTS[lang]["btn_text"]], [TEXTS[lang]["btn_time"]], [TEXTS[lang]["btn_del"]]]
    await update.message.reply_text(TEXTS[lang]["edit_type"], reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True))
    return TAHRIR_TURI

async def tahrir_turi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    lang = users[uid]["lang"]
    choice = update.message.text
    if choice == TEXTS[lang]["btn_del"]:
        users[uid]["edit"]["task"].cancel()
        users[uid]["reminders"].remove(users[uid]["edit"])
        users[uid].pop("edit")
        return await menu(update, context)
    users[uid]["edit_type"] = choice
    await update.message.reply_text(TEXTS[lang]["edit_val"], reply_markup=ReplyKeyboardRemove())
    return TAHRIR_KIRITISH

async def tahrir_kirit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    lang = users[uid]["lang"]
    r = users[uid]["edit"]
    try:
        if users[uid]["edit_type"] == TEXTS[lang]["btn_time"]:
            r["time"] = datetime.strptime(update.message.text, "%d.%m.%Y %H:%M")
        else:
            r["text"] = update.message.text
        r["task"].cancel()
        r["task"] = asyncio.create_task(schedule(uid, r, context))
        users[uid].pop("edit")
        return await menu(update, context)
    except:
        await update.message.reply_text(TEXTS[lang]["error_fmt"])
        return TAHRIR_KIRITISH

def main():
    app = Application.builder().token(TOKEN).build()
    conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            TIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, til)],
            MINTQA: [MessageHandler(filters.TEXT & ~filters.COMMAND, mintqa)],
            MENU: [MessageHandler(filters.TEXT & ~filters.COMMAND, menu_handler)],
            TUR: [MessageHandler(filters.TEXT & ~filters.COMMAND, tur)],
            TARGET_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, target_id)],
            MATN: [MessageHandler(filters.TEXT & ~filters.COMMAND, matn)],
            VAQT: [MessageHandler(filters.TEXT & ~filters.COMMAND, vaqt)],
            QAYTA: [MessageHandler(filters.TEXT & ~filters.COMMAND, qayta)],
            TAHRIR_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, tahrir_id)],
            TAHRIR_TURI: [MessageHandler(filters.TEXT & ~filters.COMMAND, tahrir_turi)],
            TAHRIR_KIRITISH: [MessageHandler(filters.TEXT & ~filters.COMMAND, tahrir_kirit)],
        },
        fallbacks=[CommandHandler("start", start)],
        allow_reentry=True,
    )
    app.add_handler(conv)
    app.run_polling()

if __name__ == "__main__":
    main()