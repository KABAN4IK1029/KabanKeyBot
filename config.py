# -*- coding: utf-8 -*-
"""Конфигурация Kaban Key Bot. Загружает настройки из .env файла."""
import os
from dotenv import load_dotenv

# Загружаем переменные из .env (если файл существует)
load_dotenv()


def get_env(key, default=None):
    """Безопасное получение переменной окружения."""
    return os.getenv(key, default)


# ==================== Telegram ====================
TELEGRAM_BOT_TOKEN = get_env("TELEGRAM_BOT_TOKEN", "")

# ==================== AWS ====================
AWS_REGION = get_env("AWS_REGION", "us-east-1")
AWS_ACCESS_KEY_ID = get_env("AWS_ACCESS_KEY_ID", None)
AWS_SECRET_ACCESS_KEY = get_env("AWS_SECRET_ACCESS_KEY", None)

# ==================== DynamoDB ====================
TABLE_KEYS = get_env("DYNAMODB_TABLE_KEYS", "kaban_keys")
TABLE_USERS = get_env("DYNAMODB_TABLE_USERS", "kaban_users")
TABLE_SETTINGS = get_env("DYNAMODB_TABLE_SETTINGS", "kaban_settings")

# ==================== Настройки ключей ====================
DEFAULT_KEY_PREFIX = get_env("DEFAULT_KEY_PREFIX", "KABAN4IK1029")
# Формат ключа: {PREFIX}-{XXXX}-{XXXX}-{XXXX}

# ==================== Админ ====================
# Первый пользователь, который напишет боту, становится админом.
# ADMIN_USER_ID можно задать в .env, если нужно зафиксировать конкретного админа.
ADMIN_USER_ID = get_env("ADMIN_USER_ID", None)
if ADMIN_USER_ID:
    ADMIN_USER_ID = int(ADMIN_USER_ID)

# ==================== Проверка ====================
def is_configured():
    """Проверяет, что все обязательные настройки заполнены."""
    return bool(TELEGRAM_BOT_TOKEN)

def missing_config():
    """Возвращает список отсутствующих настроек."""
    missing = []
    if not TELEGRAM_BOT_TOKEN:
        missing.append("TELEGRAM_BOT_TOKEN")
    return missing