# -*- coding: utf-8 -*-
"""Мастер первичной настройки Kaban Key Bot.
Запускается один раз после установки: python setup_wizard.py"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV_FILE = os.path.join(ROOT, ".env")
ENV_EXAMPLE = os.path.join(ROOT, ".env.example")


def print_header():
    print("=" * 60)
    print("   KABAN KEY BOT — МАСТЕР НАСТРОЙКИ")
    print("=" * 60)
    print()


def copy_example():
    if os.path.exists(ENV_FILE):
        print(f"[!] Файл .env уже существует. Пропускаем копирование.")
        return
    if os.path.exists(ENV_EXAMPLE):
        with open(ENV_EXAMPLE, "r", encoding="utf-8") as f:
            content = f.read()
        with open(ENV_FILE, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"[+] Создан файл .env из шаблона .env.example")
    else:
        print("[!] Не найден .env.example")


def ask(prompt, default=""):
    if default:
        prompt = f"{prompt} [{default}]: "
    else:
        prompt = f"{prompt}: "
    val = input(prompt).strip()
    return val if val else default


def edit_env():
    print("\n--- Заполнение конфигурации ---")
    print("Вот что нужно ввести:\n")
    print("1. TELEGRAM_BOT_TOKEN — токен бота от @BotFather")
    print("2. AWS_REGION — регион AWS (по умолчанию us-east-1)")
    print("3. AWS_ACCESS_KEY_ID / AWS_SECRET_ACCESS_KEY — ключи доступа AWS")
    print("4. DEFAULT_KEY_PREFIX — префикс ключей (по умолчанию KABAN4IK1029)\n")

    token = ask("Введите TELEGRAM_BOT_TOKEN (от @BotFather)", "")
    region = ask("Введите AWS_REGION", "us-east-1")
    access_key = ask("Введите AWS_ACCESS_KEY_ID (или Enter для пропуска)", "")
    secret_key = ask("Введите AWS_SECRET_ACCESS_KEY (или Enter для пропуска)", "")
    prefix = ask("Введите DEFAULT_KEY_PREFIX", "KABAN4IK1029")

    # Читаем текущий .env
    lines = []
    if os.path.exists(ENV_FILE):
        with open(ENV_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()

    replacements = {
        "TELEGRAM_BOT_TOKEN=": f"TELEGRAM_BOT_TOKEN={token}",
        "AWS_REGION=": f"AWS_REGION={region}",
        "AWS_ACCESS_KEY_ID=": f"AWS_ACCESS_KEY_ID={access_key}",
        "AWS_SECRET_ACCESS_KEY=": f"AWS_SECRET_ACCESS_KEY={secret_key}",
        "DEFAULT_KEY_PREFIX=": f"DEFAULT_KEY_PREFIX={prefix}",
    }

    new_lines = []
    for line in lines:
        replaced = False
        for key, value in replacements.items():
            if line.startswith(key):
                new_lines.append(value + "\n")
                replaced = True
                break
        if not replaced:
            new_lines.append(line)

    with open(ENV_FILE, "w", encoding="utf-8") as f:
        f.writelines(new_lines)

    print(f"\n[+] Конфигурация сохранена в {ENV_FILE}")
    print("\nТеперь запустите бота: python bot/main.py")


def main():
    print_header()
    copy_example()
    edit_env()


if __name__ == "__main__":
    main()