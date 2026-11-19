# -*- coding: utf-8 -*-
"""Генерация и проверка ключей формата PREFIX-XXXX-XXXX-XXXX."""
import random
import string
import time
from config import DEFAULT_KEY_PREFIX


def generate_suffix(length=4):
    """Генерирует случайный блок из букв и цифр."""
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choice(chars) for _ in range(length))


def generate_key(prefix=None):
    """
    Генерирует ключ в формате: PREFIX-XXXX-XXXX-XXXX
    Например: KABAN4IK1029-A1B2-C3D4-E5F6
    """
    if prefix is None:
        prefix = DEFAULT_KEY_PREFIX
    # Убираем дефисы из префикса, если они есть
    prefix = prefix.replace("-", "")
    s1 = generate_suffix(4)
    s2 = generate_suffix(4)
    s3 = generate_suffix(4)
    return f"{prefix}-{s1}-{s2}-{s3}"


def parse_key(key):
    """
    Разбирает ключ на части.
    Возвращает dict с ключами: prefix, s1, s2, s3, full
    Или None, если ключ не соответствует формату.
    """
    parts = key.strip().split("-")
    if len(parts) != 4:
        return None
    prefix, s1, s2, s3 = parts
    # Проверяем, что суффиксы из 4 символов each
    if len(s1) != 4 or len(s2) != 4 or len(s3) != 4:
        return None
    return {
        "prefix": prefix,
        "s1": s1,
        "s2": s2,
        "s3": s3,
        "full": key.strip(),
    }


def is_valid_format(key):
    """Проверяет, что ключ соответствует формату PREFIX-XXXX-XXXX-XXXX."""
    return parse_key(key) is not None