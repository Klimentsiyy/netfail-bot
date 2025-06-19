
# NetFail Bot

🛰 **NetFail** — это Telegram-бот, который отслеживает сбои в работе популярных сервисов и публикует уведомления в Telegram-канал.

## 🔍 Что делает бот

- Проверяет состояние более 40+ сервисов (YouTube, Telegram, TikTok, Reddit и др.)
- Анализирует пинг и делает прогнозы стабильности сети
- Показывает сбои с географией (если доступна)
- Публикует автоматические дайджесты и исторические отчёты
- Умеет перезапускаться и останавливаться по команде
- Работает на `aiogram`, `aiohttp`, `BeautifulSoup`, `ping3`, `apscheduler`

## 🚀 Запуск

```bash
python netfail_bot.py
```

## 🛠️ Зависимости

Создай `requirements.txt` с зависимостями:

```text
aiogram
aiohttp
beautifulsoup4
ping3
apscheduler
```

## 📡 Канал

Пример: [@NetFailNews](https://t.me/NetFailNews) — все уведомления отправляются сюда.

---

🤖 Автор: [@klimentsiternovskiy](https://t.me/klimentsiternovskiy)  
Лицензия: MIT
