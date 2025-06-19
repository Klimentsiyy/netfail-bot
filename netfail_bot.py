import asyncio
import aiohttp
import sys
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.exceptions import TelegramAPIError
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from bs4 import BeautifulSoup
import datetime
import logging
from datetime import timezone
from ping3 import ping
import random

API_TOKEN = "8038386486:AAHLk9soGCyGHmvOruPfu_suHTU5CK2jozc"
CHANNEL_ID = -1002810095633

SERVICES = {
    "WhatsApp": {"type": "isitdown", "domain": "whatsapp.com"},
    "Reddit": {"type": "isitdown", "domain": "reddit.com"},
    "Twitter": {"type": "isitdown", "domain": "twitter.com"},
    "Comcast": {"type": "isitdown", "domain": "comcast.com"},
    "Netflix": {"type": "isitdown", "domain": "netflix.com"},
    "Facebook": {"type": "isitdown", "domain": "facebook.com"},
    "YouTube": {"type": "isitdown", "domain": "youtube.com"},
    "Instagram": {"type": "isitdown", "domain": "instagram.com"},
    "Gmail": {"type": "isitdown", "domain": "mail.google.com"},
    "Dropbox": {"type": "isitdown", "domain": "dropbox.com"},
    "Steam": {"type": "isitdown", "domain": "steamcommunity.com"},
    "Pinterest": {"type": "isitdown", "domain": "pinterest.com"},
    "Amazon": {"type": "isitdown", "domain": "amazon.com"},
    "Tumblr": {"type": "isitdown", "domain": "tumblr.com"},
    "Xbox": {"type": "isitdown", "domain": "xbox.com"},
    "Paypal": {"type": "isitdown", "domain": "paypal.com"},
    "Twitch": {"type": "isitdown", "domain": "twitch.tv"},
    "Spotify": {"type": "statuspage", "url": "https://spotify.statuspage.io/api/v2/status.json", "statuspage_api": "https://spotify.statuspage.io/api/v2/incidents/unresolved.json"},
    "GitHub": {"type": "statuspage", "url": "https://www.githubstatus.com/api/v2/status.json", "statuspage_api": "https://www.githubstatus.com/api/v2/incidents/unresolved.json"},
    "OpenAI": {"type": "statuspage", "url": "https://status.openai.com/api/v2/status.json", "statuspage_api": "https://status.openai.com/api/v2/incidents/unresolved.json"},
    "Cloudflare": {"type": "statuspage", "url": "https://www.cloudflarestatus.com/api/v2/status.json", "statuspage_api": "https://www.cloudflarestatus.com/api/v2/incidents/unresolved.json"},
    "Telegram": {"type": "isitdown", "domain": "web.telegram.org"},
    "TikTok": {"type": "isitdown", "domain": "tiktok.com"},
    "Zoom": {"type": "isitdown", "domain": "zoom.us"},
    "Snapchat": {"type": "isitdown", "domain": "snapchat.com"},
    "Apple": {"type": "isitdown", "domain": "apple.com"},
    "LinkedIn": {"type": "isitdown", "domain": "linkedin.com"},
    "Battle.net": {"type": "isitdown", "domain": "battle.net"},
    "Roblox": {"type": "isitdown", "domain": "roblox.com"},
    "HBO Max": {"type": "isitdown", "domain": "hbomax.com"},
    "Epic Games": {"type": "isitdown", "domain": "epicgames.com"},
    "Discord": {"type": "isitdown", "domain": "discord.com"},
    "Google": {"type": "isitdown", "domain": "google.com"},
    "Slack": {"type": "isitdown", "domain": "slack.com"},
    "Microsoft Teams": {"type": "isitdown", "domain": "teams.microsoft.com"},
    "Dropbox Business": {"type": "isitdown", "domain": "dropboxbusiness.com"},
    "Salesforce": {"type": "isitdown", "domain": "salesforce.com"},
    "Bitbucket": {"type": "statuspage", "url": "https://bitbucket.status.atlassian.com/api/v2/status.json", "statuspage_api": "https://bitbucket.status.atlassian.com/api/v2/incidents/unresolved.json"},
    "Atlassian": {"type": "statuspage", "url": "https://status.atlassian.com/api/v2/status.json", "statuspage_api": "https://status.atlassian.com/api/v2/incidents/unresolved.json"},
    "Heroku": {"type": "statuspage", "url": "https://status.heroku.com/api/v4/current-status", "statuspage_api": "https://status.heroku.com/api/v4/incidents"},
    "Trello": {"type": "statuspage", "url": "https://trello.status.atlassian.com/api/v2/status.json", "statuspage_api": "https://trello.status.atlassian.com/api/v2/incidents/unresolved.json"},
    "Marriott": {"type": "isitdown", "domain": "marriott.com"},
    "Yandex": {"type": "isitdown", "domain": "yandex.ru"},
    "VK": {"type": "isitdown", "domain": "vk.com"},
}

PING_HOSTS = {
    name: info["domain"]
    for name, info in SERVICES.items()
    if info["type"] == "isitdown"
}

CHECK_INTERVAL = 120
REMOVE_AFTER = 3600

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

bot = Bot(token=API_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher()
scheduler = AsyncIOScheduler()

state = {
    svc: {
        "ok": True,
        "msg_id": None,
        "down_at": None,
        "history": [],
        "last_warn": {"level": "normal"}
    }
    for svc in SERVICES
}

COUNTRY_FLAG_MAP = {
    "USA": "🇺🇸",
    "United States": "🇺🇸",
    "UK": "🇬🇧",
    "United Kingdom": "🇬🇧",
    "Canada": "🇨🇦",
    "Germany": "🇩🇪",
    "France": "🇫🇷",
    "Netherlands": "🇳🇱",
    "Australia": "🇦🇺",
    "Russia": "🇷🇺",
    "Japan": "🇯🇵",
    "India": "🇮🇳",
    "Brazil": "🇧🇷",
}

def parse_geo_with_flags(geo_text: str) -> str:
    try:
        parts = geo_text.split(",")
        result_parts = []
        for part in parts:
            part = part.strip()
            if "-" in part:
                country_part, percent_part = part.split("-", 1)
                country = country_part.strip()
                percent = percent_part.strip()
                flag = COUNTRY_FLAG_MAP.get(country, "")
                if flag:
                    result_parts.append(f"{flag} {country} — {percent}")
                else:
                    result_parts.append(f"{country} — {percent}")
            else:
                result_parts.append(part)
        return "\n".join(result_parts)
    except Exception as e:
        logging.error(f"Ошибка парсинга гео данных: {e}")
        return ""

async def fetch_isitdown_status(session, domain):
    url = f"https://www.isitdownrightnow.com/{domain}.html"
    geo_info = None
    try:
        async with session.get(url, timeout=10) as resp:
            if resp.status != 200:
                return None, None
            text = await resp.text()
            soup = BeautifulSoup(text, "html.parser")
            status_div = soup.find("div", {"id": "status"})
            if status_div:
                txt = status_div.get_text(separator=" ", strip=True).lower()
                if "is up" in txt:
                    return True, None
                elif "is down" in txt:
                    geo_info = None
                    geo_div = soup.find("div", class_="mapStats")
                    if geo_div:
                        raw_geo = geo_div.get_text(separator=" ", strip=True)
                        geo_info = parse_geo_with_flags(raw_geo)
                    return False, geo_info
            up_div = soup.find("div", class_="up")
            down_div = soup.find("div", class_="down")
            if up_div:
                return True, None
            if down_div:
                geo_div = soup.find("div", class_="mapStats")
                if geo_div:
                    raw_geo = geo_div.get_text(separator=" ", strip=True)
                    geo_info = parse_geo_with_flags(raw_geo)
                return False, geo_info
    except Exception as e:
        logging.error(f"{domain}: ошибка при парсинге isitdownrightnow: {e}")
    return None, None

async def fetch_statuspage_status(session, url):
    try:
        async with session.get(url, timeout=10) as resp:
            if resp.status != 200:
                return None
            data = await resp.json()
            indicator = data.get("status", {}).get("indicator", "")
            return indicator == "none"
    except Exception as e:
        logging.error(f"{url}: ошибка при парсинге statuspage.io: {e}")
    return None

async def fetch_status(session, service):
    info = SERVICES[service]
    if info["type"] == "isitdown":
        return await fetch_isitdown_status(session, info["domain"])
    elif info["type"] == "statuspage":
        ok = await fetch_statuspage_status(session, info["url"])
        return ok, None
    return None, None

def analyze_ping(name):
    host = PING_HOSTS.get(name)
    if not host:
        return None
    try:
        rtt = ping(host, timeout=2)
        return rtt
    except Exception as e:
        logging.error(f"{name}: ошибка при пинге: {e}")
        return None

async def fetch_maintenance(session, service):
    info = SERVICES.get(service)
    if not info or info.get("type") != "statuspage":
        return []
    if service == "OpenAI":  # отключаем для OpenAI из-за проблем с JSON
        return []
    url = info.get("statuspage_api")
    if not url:
        return []
    try:
        async with session.get(url, timeout=10) as resp:
            if resp.status != 200:
                return []
            data = await resp.json()

            # Особая обработка для Heroku — data это список инцидентов
            if service == "Heroku":
                maintenance_events = []
                for inc in data:
                    if inc.get("monitoring_at") or inc.get("scheduled_for"):
                        maintenance_events.append({
                            "name": inc.get("name"),
                            "status": inc.get("status"),
                            "scheduled_for": inc.get("scheduled_for"),
                            "updated_at": inc.get("updated_at"),
                            "impact": inc.get("impact"),
                            "shortlink": inc.get("shortlink"),
                            "updates": inc.get("incident_updates", []),
                        })
                return maintenance_events

            # Для остальных сервисов стандартный разбор
            incidents = data.get("incidents", [])
            maintenance_events = []
            for inc in incidents:
                if inc.get("monitoring_at") or inc.get("scheduled_for"):
                    maintenance_events.append({
                        "name": inc.get("name"),
                        "status": inc.get("status"),
                        "scheduled_for": inc.get("scheduled_for"),
                        "updated_at": inc.get("updated_at"),
                        "impact": inc.get("impact"),
                        "shortlink": inc.get("shortlink"),
                        "updates": inc.get("incident_updates", []),
                    })
            return maintenance_events
    except Exception as e:
        logging.error(f"{service} maintenance fetch error: {e}")
    return []

async def check_services():
    async with aiohttp.ClientSession() as session:
        for name in SERVICES:
            if SERVICES[name]["type"] == "statuspage":
                maintenance = await fetch_maintenance(session, name)
                for event in maintenance:
                    key = f"{name}_maintenance_{event['updated_at']}"
                    if key not in state:
                        state[key] = True
                        sched_time = event.get("scheduled_for") or event.get("updated_at")
                        dt_str = sched_time.split("T")[0] if sched_time else "неизвестно"
                        text = (
                            f"🛠️ <b>Плановое техобслуживание:</b>\n"
                            f"<b>{name}</b>\n"
                            f"Статус: <i>{event['status']}</i>\n"
                            f"Начало: {dt_str}\n"
                            f"Подробнее: <a href='{event.get('shortlink', '')}'>ссылка</a>"
                        )
                        await bot.send_message(CHANNEL_ID, text)

        for name in SERVICES:
            ok, geo = await fetch_status(session, name)
            if ok is None:
                continue
            prev = state[name]["ok"]
            now = ok

            ping_rtt = analyze_ping(name)
            warn_text = ""
            warn_level = "normal"
            if ping_rtt is not None:
                ms = ping_rtt * 1000
                if ms > 500:
                    warn_text = f"⚠️ <b>Высокий пинг</b>: <code>{int(ms)} мс</code> — возможны перебои."
                    warn_level = "high"
                elif ms < 20:
                    warn_text = f"✅ <b>Сеть стабильна</b>: пинг <code>{int(ms)} мс</code>."
                    warn_level = "low"
            if warn_level != state[name]["last_warn"]["level"]:
                if warn_text:
                    await bot.send_message(CHANNEL_ID, f"<b>🔔 Предупреждение:</b>\n{name}: {warn_text}")
                    logging.info(f"{name}: предупреждение отправлено ({warn_level})")
                state[name]["last_warn"]["level"] = warn_level

            if prev and not now:
                t = datetime.datetime.now(timezone.utc).strftime("%H:%M UTC, %d.%m.%Y")
                geo_str = f"\n🌍 <i>Проблемы зафиксированы в регионах:</i>\n<code>{geo}</code>" if geo else ""

                jokes = [
                    "Ну всё, опять интернет гуляет...",
                    "Кажется, кто-то забыл заплатить за хостинг 😅",
                    "Всё ломается, но мы держимся!",
                    "Сервис ушёл на обед — ждём обратно.",
                    "Похоже, сервер решил взять выходной.",
                    "Наш бот шутит: 'Пусть будет сбой — будет повод отдохнуть!'",
                ]
                joke = random.choice(jokes)

                msg = await bot.send_message(CHANNEL_ID,
                    f"‼️ <b>{name}</b> – проблемы с подключением ‼️\n\n"
                    f"Сервис <b>{name}</b> сейчас недоступен.\n"
                    f"{geo_str}\n"
                    f"🕒 Время фикса: {t}\n\n"
                    f"🤖 <i>{joke}</i>"
                )
                state[name]["ok"] = False
                state[name]["msg_id"] = msg.message_id
                state[name]["down_at"] = datetime.datetime.now(timezone.utc)
                state[name]["history"].append({"down": state[name]["down_at"], "up": None})
                logging.warning(f"{name}: сбой зафиксирован")

            elif not prev and now:
                t = datetime.datetime.now(timezone.utc).strftime("%H:%M UTC, %d.%m.%Y")
                await bot.send_message(CHANNEL_ID,
                    f"✅ <b>{name}</b> восстановлен ✅\n\n"
                    f"Сервис <b>{name}</b> снова доступен. Время восстановления: {t}\n"
                )
                state[name]["ok"] = True
                old_msg_id = state[name]["msg_id"]
                if old_msg_id:
                    scheduler.add_job(delete_msg, args=(CHANNEL_ID, old_msg_id),
                                      trigger="date",
                                      run_date=datetime.datetime.now(timezone.utc) + datetime.timedelta(seconds=REMOVE_AFTER))
                # Обновляем историю
                for record in reversed(state[name]["history"]):
                    if record["up"] is None:
                        record["up"] = datetime.datetime.now(timezone.utc)
                        break

    issues = [name for name, data in state.items() if not data["ok"]]
    if issues:
        logging.info(f"Мониторинг провел — есть проблемы с сервисами: {', '.join(issues)}")
    else:
        logging.info("Мониторинг провел — все исправно")

async def delete_msg(chat_id, message_id):
    try:
        await bot.delete_message(chat_id, message_id)
        logging.info(f"Удалено сообщение {message_id}")
    except TelegramAPIError:
        pass

async def daily_digest():
    now = datetime.datetime.now(timezone.utc)
    date_str = now.strftime("%d.%m.%Y")
    report = []
    for svc, data in state.items():
        if not data["ok"]:
            down_time = data["down_at"].strftime("%H:%M UTC, %d.%m.%Y") if data["down_at"] else "неизвестно"
            report.append(f"<b>{svc}</b> — ⛔️ ПРОБЛЕМА с {down_time}")
    if not report:
        text = f"📅 <b>Дайджест на {date_str}:</b>\nВсе сервисы работают стабильно."
    else:
        text = f"📅 <b>Дайджест на {date_str}:</b>\nПроблемы зафиксированы:\n" + "\n".join(report)
    await bot.send_message(CHANNEL_ID, text)

async def historical_fail():
    yesterday = datetime.datetime.now(timezone.utc).date() - datetime.timedelta(days=1)
    report = []
    for svc, data in state.items():
        for h in data["history"]:
            if h["down"].date() == yesterday:
                up_str = h["up"].strftime("%H:%M UTC, %d.%m.%Y") if h["up"] else "ещё не восстановлен"
                down_str = h["down"].strftime("%H:%M UTC, %d.%m.%Y")
                report.append(f"<b>{svc}</b>: сбой с {down_str} по {up_str}")
    if report:
        text = "📅 <b>Исторический сбой за вчера:</b>\n\n" + "\n".join(report)
        await bot.send_message(CHANNEL_ID, text)

async def command_listener():
    while True:
        command = await asyncio.to_thread(input, "Введите команду (stop/restart): ")
        command = command.strip().lower()
        if command == "stop":
            await bot.send_message(CHANNEL_ID, "🛑 Бот остановлен вручную.")
            logging.info("Остановка бота по команде stop")
            await bot.close()
            scheduler.shutdown()
            sys.exit(0)
        elif command == "restart":
            await bot.send_message(CHANNEL_ID, "🔄 Перезапуск бота вручную.")
            logging.info("Перезапуск бота по команде restart")
            await bot.close()
            scheduler.shutdown()
            sys.exit(0)
        else:
            print("Неизвестная команда. Введите 'stop' или 'restart'.")

async def periodic():
    while True:
        await check_services()
        await asyncio.sleep(CHECK_INTERVAL)

async def main():
    logging.info("Бот запускается...")
    scheduler.add_job(daily_digest, CronTrigger(hour=21, minute=0))
    scheduler.add_job(historical_fail, CronTrigger(hour=21, minute=5))
    scheduler.start()
    asyncio.create_task(periodic())
    asyncio.create_task(command_listener())
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
