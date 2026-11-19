# -*- coding: utf-8 -*-
"""Обработчики команд бота."""
import telebot
from telebot import types
from config import is_configured, missing_config
from keygen import is_valid_format
from admin_panel import AdminPanel


def register_handlers(bot, db, is_admin_func):
    admin_panel = AdminPanel(bot, db, is_admin_func)

    if not is_configured():
        print("=" * 60)
        print("⚠️  ВНИМАНИЕ: Не настроен TELEGRAM_BOT_TOKEN!")
        print("   Заполните файл .env (см. .env.example)")
        print("   Отсутствуют:", ", ".join(missing_config()))
        print("=" * 60)

    @bot.message_handler(commands=["start"])
    def cmd_start(message):
        user_id = message.from_user.id
        username = message.from_user.username or message.from_user.first_name or "unknown"
        existing = db.get_user(user_id)
        if not existing:
            admins = db.list_admins()
            is_first = len(admins) == 0
            db.create_user(user_id, username, is_admin=is_first)
            if is_first:
                bot.reply_to(
                    message,
                    "👋 <b>Добро пожаловать!</b>\n\nВы стали <b>АДМИНОМ</b> (первый пользователь).\nИспользуйте /admin для панели управления.\n/help — команды.",
                    parse_mode="HTML",
                )
            else:
                bot.reply_to(message, "👋 <b>Добро пожаловать!</b>\nИспользуйте /help для команд.", parse_mode="HTML")
        else:
            bot.reply_to(message, "👋 С возвращением! /help — команды.", parse_mode="HTML")

    @bot.message_handler(commands=["help"])
    def cmd_help(message):
        user_id = message.from_user.id
        is_admin = is_admin_func(user_id)
        text = ("📋 <b>КОМАНДЫ</b>\n──────────────\n/start — запуск\n/help — справка\n"
                "/key <код> — активировать ключ\n/mykey — ваши ключи\n/status — статус системы\n")
        if is_admin:
            text += ("\n🛠 <b>АДМИН:</b>\n/admin — панель\n/genkey — ключ\n/prefix <префикс> — смена префикса\n"
                     "/stats — статистика\n/admins — админы\n")
        bot.reply_to(message, text, parse_mode="HTML")

    @bot.message_handler(commands=["admin"])
    def cmd_admin(message):
        user_id = message.from_user.id
        if not is_admin_func(user_id):
            bot.reply_to(message, "⛔ Доступ только для админа!")
            return
        admin_panel.send_admin_menu(message.chat.id)

    @bot.message_handler(commands=["genkey"])
    def cmd_genkey(message):
        user_id = message.from_user.id
        if not is_admin_func(user_id):
            bot.reply_to(message, "⛔ Доступ только для админа!")
            return
        from keygen import generate_key
        prefix = db.get_key_prefix()
        key = generate_key(prefix)
        if db.create_key(key, prefix, user_id, message.from_user.username):
            bot.reply_to(message, f"✅ Ключ: <code>{key}</code>\nПрефикс: <code>{prefix}</code>", parse_mode="HTML")
        else:
            bot.reply_to(message, "❌ Ошибка при создании ключа.")

    @bot.message_handler(commands=["prefix"])
    def cmd_prefix(message):
        user_id = message.from_user.id
        if not is_admin_func(user_id):
            bot.reply_to(message, "⛔ Доступ только для админа!")
            return
        parts = message.text.split(maxsplit=1)
        if len(parts) < 2:
            bot.reply_to(message, f"Префикс: <code>{db.get_key_prefix()}</code>\nИспользование: /prefix НОВЫЙ_ПРЕФИКС", parse_mode="HTML")
            return
        new_prefix = parts[1].strip()
        if "-" in new_prefix or " " in new_prefix or len(new_prefix) < 3:
            bot.reply_to(message, "❌ Неверный формат префикса.")
            return
        if db.set_key_prefix(new_prefix):
            bot.reply_to(message, f"✅ Новый префикс: <code>{new_prefix}</code>", parse_mode="HTML")
        else:
            bot.reply_to(message, "❌ Ошибка сохранения.")

    @bot.message_handler(commands=["stats"])
    def cmd_stats(message):
        user_id = message.from_user.id
        if not is_admin_func(user_id):
            bot.reply_to(message, "⛔ Доступ только для админа!")
            return
        total = db.count_keys()
        unused = db.count_keys("unused")
        active = db.count_keys("active")
        bot.reply_to(message, f"📊 Всего: {total}\nДоступно: {unused}\nАктивных: {active}\nПрефикс: {db.get_key_prefix()}", parse_mode="HTML")

    @bot.message_handler(commands=["admins"])
    def cmd_admins(message):
        user_id = message.from_user.id
        if not is_admin_func(user_id):
            bot.reply_to(message, "⛔ Доступ только для админа!")
            return
        admins = db.list_admins()
        text = "👥 <b>АДМИНЫ:</b>\n"
        if admins:
            for a in admins:
                name = a.get("username", "") or a.get("user_id", "?")
                text += f"• @{name} (ID: <code>{a['user_id']}</code>)\n"
        else:
            text += "Админов не найдено.\n"
        bot.reply_to(message, text, parse_mode="HTML")

    @bot.message_handler(commands=["key"])
    def cmd_key(message):
        user_id = message.from_user.id
        username = message.from_user.username or message.from_user.first_name or "unknown"
        parts = message.text.split(maxsplit=1)
        if len(parts) < 2:
            bot.reply_to(message, "Использование: /key <ВАШ_КЛЮЧ>\nПример: /key KABAN4IK1029-A1B2-C3D4-E5F6")
            return
        key_value = parts[1].strip().upper()
        if not is_valid_format(key_value):
            bot.reply_to(message, "❌ Неверный формат ключа. Ожидается: PREFIX-XXXX-XXXX-XXXX")
            return
        key_info = db.get_key(key_value)
        if not key_info:
            bot.reply_to(message, "❌ Ключ не найден.")
            return
        if key_info.get("status") != "unused":
            bot.reply_to(message, "❌ Этот ключ уже использован.")
            return
        if db.activate_key(key_value, user_id, username):
            bot.reply_to(message, f"✅ Ключ активирован!\n<code>{key_value}</code>", parse_mode="HTML")
        else:
            bot.reply_to(message, "❌ Ошибка при активации ключа.")

    @bot.message_handler(commands=["mykey"])
    def cmd_mykey(message):
        user_id = message.from_user.id
        keys = db.list_keys(limit=100)
        user_keys = [k for k in keys if k.get("activated_by") == str(user_id)]
        if not user_keys:
            bot.reply_to(message, "У вас нет активированных ключей.")
            return
        text = "🔑 <b>ВАШИ КЛЮЧИ:</b>\n"
        for k in user_keys[:5]:
            text += f"• <code>{k['key']}</code>\n"
        bot.reply_to(message, text, parse_mode="HTML")

    @bot.message_handler(commands=["status"])
    def cmd_status(message):
        total = db.count_keys()
        unused = db.count_keys("unused")
        active = db.count_keys("active")
        bot.reply_to(message, f"📡 <b>СТАТУС:</b>\nВсего: {total}\nДоступно: {unused}\nИспользовано: {active}\nПрефикс: {db.get_key_prefix()}", parse_mode="HTML")

    @bot.callback_query_handler(func=lambda call: call.data and call.data.startswith("admin_"))
    def cb_admin(call):
        admin_panel.handle_callback(call)

    @bot.message_handler(func=lambda message: True, content_types=["text"])
    def handle_text(message):
        if message.text.startswith("/"):
            bot.reply_to(message, "Неизвестная команда. Используйте /help для списка команд.")