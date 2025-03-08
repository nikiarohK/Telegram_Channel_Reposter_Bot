import asyncio
import json
import logging
from telethon import TelegramClient, events, utils
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message
from config import api_id, api_hash, bot_token, api_ai
from telethon import types
from openai import AsyncOpenAI


# Настройка логирования
logging.basicConfig(
    format='[%(levelname)s] %(asctime)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Файл для хранения данных
CHANNELS_FILE = "channels.json"

# Инициализация клиентов
telethon_client = TelegramClient('anon', api_id, api_hash)
bot = Bot(token=bot_token)
dp = Dispatcher()

def load_channels():
    try:
        with open(CHANNELS_FILE, "r") as f:
            data = json.load(f)
            return (
                set(map(str, data.get("active_channels", []))),
                str(data.get("main_channel_id")) if data.get("main_channel_id") else None,
                data.get("prompt", "Перепиши текст своими словами, но не меняй суть")  # Загрузка промпта
            )
    except (FileNotFoundError, json.JSONDecodeError):
        return set(), None, "Перепиши текст своими словами, но не меняй суть"
    except Exception as e:
        logger.error(f"Ошибка загрузки: {e}")
        return set(), None, "Перепиши текст своими словами, но не меняй суть"

def save_channels():
    data = {
        "active_channels": list(active_channels),
        "main_channel_id": main_channel_id,
        "prompt": current_prompt  # Сохранение промпта
    }
    try:
        with open(CHANNELS_FILE, "w") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        logger.error(f"Ошибка сохранения: {e}")

# Инициализация переменных
active_channels, main_channel_id, current_prompt = load_channels()

async def get_channel_id(link: str) -> str:
    """Получение корректного ID канала в формате строки"""
    try:
        entity = await telethon_client.get_entity(link)
        return str(utils.get_peer_id(entity))
    except Exception as e:
        logger.error(f"Ошибка получения ID: {e}")
        return None

@dp.message(Command("start", "help"))
async def start_command(message: Message):
    help_text = (
        "🤖 Бот для пересылки сообщений между каналами\n\n"
        "🔹 Основные команды:\n"
        "/main_channel [ссылка] - Установить основной канал\n"
        "/add_channel [ссылка] - Добавить канал для отслеживания\n"
        "/remove [ссылка] - Удалить канал из отслеживания\n"
        "/list - Показать отслеживаемые каналы\n"
        "/id [ссылка] - Показать ID канала\n"
        "/status - Проверить состояние бота\n"
        "/change_promt [текст] - Изменить промпт для переписывания\n"
        "/show_promt - Показать текущий промпт"
    )
    await message.answer(help_text)

@dp.message(Command("id"))
async def show_id(message: Message):
    args = message.text.split()
    if len(args) < 2:
        return await message.reply("❌ Укажите ссылку на канал")
    
    channel_id = await get_channel_id(args[1])
    if channel_id:
        await message.reply(f"🆔 ID канала: `{channel_id}`", parse_mode="Markdown")
    else:
        await message.reply("❌ Не удалось получить ID канала")

@dp.message(Command("main_channel"))
async def set_main_channel(message: Message):
    global main_channel_id
    args = message.text.split()
    
    if len(args) < 2:
        return await message.reply("❌ Укажите ссылку на канал")
    
    channel_id = await get_channel_id(args[1])
    if not channel_id:
        return await message.reply("❌ Канал не найден")

    try:
        await telethon_client.send_message(entity=int(channel_id), message="🔒 Проверка прав доступа...")
    except Exception as e:
        return await message.reply(f"❌ Нет прав доступа: {e}")
    
    main_channel_id = channel_id
    save_channels()
    await message.reply(f"✅ Основной канал установлен: `{channel_id}`", parse_mode="Markdown")

async def get_channel_id(link: str) -> int:
    """Получение ID канала с обработкой ошибок"""
    try:
        # Чистим ссылку от лишних символов
        link = link.strip().replace("https://t.me/", "").replace("@", "")
        
        # Пробуем получить сущность канала
        entity = await telethon_client.get_entity(link)
        
        # Проверяем тип объекта
        if isinstance(entity, (types.Channel, types.Chat)):
            return utils.get_peer_id(entity)
            
        return None
    except ValueError:
        # Пробуем присоединиться к каналу, если не получилось найти
        try:
            await telethon_client.join_channel(link)
            entity = await telethon_client.get_entity(link)
            return utils.get_peer_id(entity)
        except Exception as e:
            logger.error(f"Ошибка доступа к каналу {link}: {str(e)}")
            return None
    except Exception as e:
        logger.error(f"Общая ошибка: {str(e)}")
        return None

@dp.message(Command("add_channel"))
async def add_channel(message: Message):
    args = message.text.split()
    if len(args) < 2:
        return await message.reply("❌ Укажите ссылку на канал")
    
    try:
        channel_id = await get_channel_id(args[1])
        if not channel_id:
            return await message.reply("❌ Канал не найден или нет доступа")

        if channel_id not in active_channels:
            active_channels.add(channel_id)
            save_channels()
            
            # Получаем название для подтверждения
            entity = await telethon_client.get_entity(channel_id)
            await message.reply(
                f"✅ Канал добавлен: {entity.title} (ID: `{channel_id}`)",
                parse_mode="Markdown"
            )
        else:
            await message.reply("ℹ️ Этот канал уже отслеживается")

    except Exception as e:
        logger.error(f"Ошибка добавления канала: {str(e)}")
        await message.reply("❌ Произошла ошибка при добавлении канала")
        
@dp.message(Command("remove"))
async def remove_channel(message: Message):
    args = message.text.split()
    if len(args) < 2:
        return await message.reply("❌ Укажите ссылку на канал")
    
    channel_id = await get_channel_id(args[1])
    if not channel_id:
        return await message.reply("❌ Канал не найден")

    if channel_id in active_channels:
        active_channels.remove(channel_id)
        save_channels()
        await message.reply(f"✅ Канал удален: `{channel_id}`", parse_mode="Markdown")
    else:
        await message.reply("ℹ️ Этот канал не отслеживается")

@dp.message(Command("list"))
async def list_channels(message: Message):
    if not active_channels:
        return await message.reply("ℹ️ Нет отслеживаемых каналов")
    
    response = ["📋 Отслеживаемые каналы:"]
    
    for idx, channel_id in enumerate(active_channels, 1):
        try:
            # Получаем информацию о канале
            entity = await telethon_client.get_entity(int(channel_id))
            title = entity.title
        except Exception as e:
            title = "Неизвестный канал"
            logger.error(f"Ошибка получения канала {channel_id}: {str(e)}")
        
        response.append(f"{idx}. {title} (ID: `{channel_id}`)")

    await message.reply("\n".join(response), parse_mode="Markdown")

@dp.message(Command("status"))
async def status_check(message: Message):
    try:
        main_channel_info = "не установлен"
        if main_channel_id:
            try:
                # Получаем информацию о основном канале
                entity = await telethon_client.get_entity(int(main_channel_id))
                main_channel_info = f"{entity.title} (ID: `{main_channel_id}`)"
            except Exception as e:
                logger.error(f"Ошибка получения информации о канале: {str(e)}")
                main_channel_info = f"ID: `{main_channel_id}` (название недоступно)"
        
        status = [
            f"📌 Основной канал: {main_channel_info}",
            f"🔢 Отслеживаемых каналов: {len(active_channels)}",
            f"📡 Состояние подключения: {'✅' if telethon_client.is_connected() else '❌'}"
        ]
        
        await message.reply("\n".join(status), parse_mode="Markdown")
        
    except Exception as e:
        logger.error(f"Ошибка в команде status: {str(e)}")
        await message.reply("❌ Произошла ошибка при получении статуса")

@dp.message(Command("change_promt"))
async def change_prompt(message: Message):
    global current_prompt
    new_prompt = message.text.replace('/change_promt', '').strip()
    
    if not new_prompt:
        return await message.reply("❌ Укажите новый промпт после команды")
    
    current_prompt = new_prompt
    save_channels()
    await message.reply(f"✅ Промпт успешно обновлен:\n`{new_prompt}`", parse_mode="Markdown")

@dp.message(Command("show_promt"))
async def show_prompt(message: Message):
    await message.reply(
        f"📝 Текущий промпт:\n`{current_prompt}`", 
        parse_mode="Markdown"
    )

client_openai = AsyncOpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=api_ai,  # Ваш ключ OpenRouter
)

async def rewrite_text(text: str) -> str:
    """Переписывает текст через OpenRouter API"""
    try:
        response = await client_openai.chat.completions.create(
            model="deepseek/deepseek-r1-zero:free",
            messages=[
                {
                    "role": "system",
                    "content": f"{current_prompt}. Не применяй никакое форматирование"  # Используем текущий промпт
                },
                {
                    "role": "user", 
                    "content": text
                }
            ],
            temperature=0.8,
            max_tokens=2000
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"OpenRouter API Error: {str(e)}")
        return None

@telethon_client.on(events.NewMessage)
async def message_handler(event):
    if not main_channel_id or str(event.chat_id) not in active_channels:
        return
    
    if event.out:
        return

    try:
        # Оригинальные данные
        original_text = event.message.text
        media = event.message.media
        entities = event.message.entities
        link_preview = isinstance(media, types.MessageMediaWebPage)

        # Модифицируем только текст
        modified_text = await rewrite_text(original_text) if original_text else None
        final_text = modified_text or original_text

        # Собираем параметры сообщения
        send_args = {
            "entity": int(main_channel_id),
            "message": final_text,
            "file": media,
            "formatting_entities": entities,
            "link_preview": link_preview
        }

        # Убираем упоминание автора для медиа
        if media and not isinstance(media, types.MessageMediaWebPage):
            send_args["silent"] = True

        await telethon_client.send_message(**send_args)
        logger.info(f"Переработано: {event.chat_id} → {main_channel_id}")

    except Exception as e:
        logger.error(f"Ошибка: {str(e)}")

async def main():
    # await telethon_client.start()
    logger.info("Telethon клиент запущен")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

