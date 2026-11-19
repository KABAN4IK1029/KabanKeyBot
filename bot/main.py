# -*- coding: utf-8 -*-
"""Kaban Key Bot — точка входа."""
import sys
import os

# Добавляем корень проекта в путь
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import telebot
from config import TELEGRAM_BOT_TOKEN, is_configured
from bot.db import DynamoDBClient
from bot.handlers import register_handlers


def is_admin(user_id):
    """Проверка прав админа. Первый пользователь = админ."""
    db = DynamoDBClient()
    return db.is_admin(user_id)


def main():
    if not is_configured():
        print("❌ ОШИБКА: Не настроен TELEGRAM_BOT_TOKEN!")
        print("   Скопируйте .env.example в .env и заполните токен.")
        print("   См. INSTALL.md для подробной инструкции.")
        sys.exit(1)

    print("🚀 Запуск Kaban Key Bot...")
    db = DynamoDBClient()

    bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN, parse_mode="HTML")
    register_handlers(bot, db, is_admin)

    print("✅ Бот запущен и готов к работе!")
    print("📝 Первый пользователь, написав боту, станет админом.")
    print("   Нажмите Ctrl+C для остановки.\n")

    bot.infinity_polling(timeout=60, long_polling_timeout=30)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n🛑 Бот остановлен пользователем.")
    except Exception as e:
        print(f"\n❌ Критическая ошибка: {e}")
        sys.exit(1)