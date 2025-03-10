```markdown
# Telegram Channel Reposter Bot 🤖

Бот для автоматической пересылки и рерайта сообщений между Telegram-каналами с использованием AI (OpenRouter).

## 📌 Основные возможности
- 🔄 Автоматическая пересылка сообщений между каналами
- ✍️ Авто-рерайт текста с сохранением смысла через ИИ
- 🛠 Простое управление каналами через чат-команды
- 💾 Автосохранение настроек между перезапусками

## ⚙️ Требования
- Python 3.10 или новее
- [OpenRouter.ai](https://openrouter.ai/) API ключ
- Telegram API ключи

## 🚀 Быстрый старт

### 1. Установка зависимостей
```bash
git clone https://github.com/nikiarohK/tg_bot.git
cd tg_bot
pip install -r requirements.txt
```

### 2. Настройка конфигурации
Создайте файл `config.py` в корне проекта:
```python
# Telegram API
api_id = "ВАШ_API_ID"          # Получить на my.telegram.org
api_hash = "ВАШ_API_HASH"      # Получить на my.telegram.org
bot_token = "ВАШ_BOT_TOKEN"    # Получить у @BotFather

# OpenRouter API
api_ai = "ВАШ_OPENROUTER_KEY"  # Получить на openrouter.ai/keys
```

### 3. Запуск бота
```bash
python main.py
```

### 4. Авторизация
После первого запуска:
1. Введите номер телефона в формате `+71234567890`
2. Введите код из Telegram/SMS
3. При наличии 2FA введите пароль

## 🕹 Команды управления
| Команда | Описание | Пример |
|---------|-----------|--------|
| `/start` | Показать справку | `/start` |
| `/main_channel` | Установить основной канал | `/main_channel https://t.me/my_channel` |
| `/add_channel` | Добавить отслеживаемый канал | `/add_channel https://t.me/source_channel` |
| `/remove` | Удалить канал | `/remove https://t.me/source_channel` |
| `/list` | Список каналов | `/list` |
| `/status` | Статус бота | `/status` |
| `/change_prompt` | Изменить промпт ИИ | `/change_prompt Перефразируй текст кратко` |
| `/show_prompt` | Изменить промпт ИИ | `/show_promt` |

## 🔧 Первоначальная настройка
1. Добавьте бота в каналы:
   - **Целевой канал** (куда пересылать) — как администратор
   - **Отслеживаемые каналы** (откуда брать) — как участник

2. Выполните в чате с ботом:
```bash
/main_channel https://t.me/ваш_основной_канал
/add_channel https://t.me/ссылка_на_остлеживаемый_канал
```

## 🛠 Решение проблем
- **"Канал не найден"**:
  - Проверьте правильность ссылки
  - Убедитесь, что бот добавлен в канал
- **Ошибки авторизации**:
  - Удалите файл `anon.session` и перезапустите бот
- **Нет пересылки сообщений**:
  - Проверьте командами `/list` и `/status`
  - Убедитесь в наличии прав у бота

## 📄 Лицензия
Проект распространяется под лицензией MIT. Подробности в файле [LICENSE](LICENSE).

---

[![Telegram API](https://img.shields.io/badge/Telegram-Bot%20API-blue)](https://core.telegram.org/bots)
[![OpenRouter](https://img.shields.io/badge/Powered%20by-OpenRouter.ai-orange)](https://openrouter.ai/)
