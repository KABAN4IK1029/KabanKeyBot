# -*- coding: utf-8 -*-
"""Админ-панель с инлайн-кнопками (по референсу AfkToken — пульт управления)."""
import telebot
from telebot import types
from config import DEFAULT_KEY_PREFIX
from keygen import generate_key, is_valid_format


class AdminPanel:
    """Админ-панель с кнопками, как пульт управления в AfkToken."""

    def __init__(self, bot, db, is_admin_func):
        self.bot = bot
        self.db = db
        self.is_admin_func = is_admin_func

    def send_admin_menu(self, chat_id, message_id=None):
        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(
            types.InlineKeyboardButton("🔑 Сгенерировать ключ", callback_data="admin_genkey"),
            types.InlineKeyboardButton("📊 Статистика", callback_data="admin_stats"),
        )
        markup.add(
            types.InlineKeyboardButton("🏷 Изменить префикс", callback_data="admin_setprefix"),
            types.InlineKeyboardButton("👥 Список админов", callback_data="admin_admins"),
        )
        markup.add(
            types.InlineKeyboardButton("📋 Последние ключи", callback_data="admin_keys"),
            types.InlineKeyboardButton("❌ Закрыть", callback_data="admin_close"),
        )
        text = (
            "🛠 <b>ПУЛЬТ УПРАВЛЕНИЯ АДМИНА</b>\n"
            "─────────────────────────\n"
            f"Текущий префикс: <code>{self.db.get_key_prefix()}</code>\n"
            "Формат ключа: <code>PREFIX-XXXX-XXXX-XXXX</code>\n\n"
            "Выберите действие:"
        )
        if message_id:
            self.bot.edit_message_text(
                text, chat_id, message_id,
                reply_markup=markup, parse_mode="HTML",
            )
        else:
            self.bot.send_message(
                chat_id, text, reply_markup=markup, parse_mode="HTML",
            )

    def handle_callback(self, call):
        data = call.data
        chat_id = call.message.chat.id
        message_id = call.message.message_id
        user_id = call.from_user.id
        if not self.is_admin_func(user_id):
            self.bot.answer_callback_query(call.id, "⛔ Доступ только для админа!")
            return
        if data == "admin_close":
            self.bot.edit_message_text(
                "✅ Панель закрыта.", chat_id, message_id, parse_mode="HTML",
            )
            self.bot.answer_callback_query(call.id)
            return
        if data == "admin_genkey":
            self._do_generate_key(chat_id, message_id, user_id, call)
        elif data == "admin_stats":
            self._do_stats(chat_id, message_id)
        elif data == "admin_setprefix":
            self._do_setprefix(chat_id, message_id)
        elif data == "admin_admins":
            self._do_admins(chat_id, message_id)
        elif data == "admin_keys":
            self._do_keys(chat_id, message_id)
        elif data == "admin_back":
            self.send_admin_menu(chat_id, message_id)

    def _do_generate_key(self, chat_id, message_id, user_id, call):
        prefix = self.db.get_key_prefix()
        key = generate_key(prefix)
        if self.db.create_key(key, prefix, user_id, call.from_user.username):
            text = (
                f"✅ <b>Ключ сгенерирован!</b>\n\n"
                f"<code>{key}</code>\n\n"
                f"Префикс: <code>{prefix}</code>\n"
                f"Статус: не используется\n\n"
                "Перешлите этот ключ пользователю для активации."
            )
            markup = types.InlineKeyboardMarkup()
            markup.add(
                types.InlineKeyboardButton("🔑 Ещё один ключ", callback_data="admin_genkey"),
                types.InlineKeyboardButton("🔙 Назад", callback_data="admin_back"),
            )
        else:
            text = "❌ Ошибка при создании ключа. Попробуйте ещё раз."
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("🔙 Назад", callback_data="admin_back"))
        self.bot.edit_message_text(
            text, chat_id, message_id,
            reply_markup=markup, parse_mode="HTML",
        )
        self.bot.answer_callback_query(call.id, f"Ключ создан: {key}")

    def _do_stats(self, chat_id, message_id):
        total = self.db.count_keys()
        unused = self.db.count_keys("unused")
        active = self.db.count_keys("active")
        admins = self.db.list_admins()
        text = (
            "📊 <b>СТАТИСТИКА СИСТЕМЫ</b>\n"
            "─────────────────────────\n"
            f"Всего ключей: <b>{total}</b>\n"
            f"Не использовано: <b>{unused}</b>\n"
            f"Активных: <b>{active}</b>\n"
            f"Админов: <b>{len(admins)}</b>\n\n"
            f"Префикс: <code>{self.db.get_key_prefix()}</code>"
        )
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🔙 Назад", callback_data="admin_back"))
        self.bot.edit_message_text(
            text, chat_id, message_id,
            reply_markup=markup, parse_mode="HTML",
        )
        self.bot.answer_callback_query(call.id if hasattr(call, 'id') else None)

    def _do_setprefix(self, chat_id, message_id):
        current = self.db.get_key_prefix()
        text = (
            f"🏷 <b>ИЗМЕНЕНИЕ ПРЕФИКСА</b>\n"
            "─────────────────────────\n"
            f"Текущий префикс: <code>{current}</code>\n\n"
            "Отправьте новый префикс одним сообщением.\n"
            "Пример: <code>KABAN4IK1029</code>\n\n"
            "Ключи будут иметь формат: <code>НОВЫЙ_ПРЕФИКС-XXXX-XXXX-XXXX</code>"
        )
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🔙 Назад", callback_data="admin_back"))
        self.bot.edit_message_text(
            text, chat_id, message_id,
            reply_markup=markup, parse_mode="HTML",
        )
        self.bot.register_next_step_handler_by_chat_id(
            chat_id, self._process_new_prefix
        )

    def _process_new_prefix(self, message):
        new_prefix = message.text.strip()
        user_id = message.from_user.id
        if not self.is_admin_func(user_id):
            self.bot.reply_to(message, "⛔ Доступ только для админа!")
            return
        if not new_prefix or len(new_prefix) < 3:
            self.bot.reply_to(message, "❌ Префикс слишком короткий (минимум 3 символа).")
            return
        if "-" in new_prefix or " " in new_prefix:
            self.bot.reply_to(message, "❌ Префикс не должен содержать дефисы и пробелы.")
            return
        if self.db.set_key_prefix(new_prefix):
            self.bot.reply_to(
                message,
                f"✅ Префикс изменён на: <code>{new_prefix}</code>",
                parse_mode="HTML",
            )
        else:
            self.bot.reply_to(message, "❌ Ошибка при сохранении префикса.")

    def _do_admins(self, chat_id, message_id):
        admins = self.db.list_admins()
        text = "👥 <b>СПИСОК АДМИНОВ</b>\n─────────────────────────\n"
        if admins:
            for a in admins:
                name = a.get("username", "") or a.get("user_id", "?")
                text += f"• @{name} (ID: <code>{a['user_id']}</code>)\n"
        else:
            text += "Админов не найдено.\n"
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🔙 Назад", callback_data="admin_back"))
        self.bot.edit_message_text(
            text, chat_id, message_id,
            reply_markup=markup, parse_mode="HTML",
        )
        self.bot.answer_callback_query(call.id if hasattr(call, 'id') else None)

    def _do_keys(self, chat_id, message_id):
        keys = self.db.list_keys(limit=10)
        text = "📋 <b>ПОСЛЕДНИЕ КЛЮЧИ</b>\n─────────────────────────\n"
        if keys:
            for k in keys:
                status_emoji = "⏳" if k.get("status") == "unused" else ("✅" if k.get("status") == "active" else "❌")
                text += (
                    f"{status_emoji} <code>{k['key']}</code>\n"
                    f"   Создал: {k.get('created_by', '?')}\n"
                    f"   Статус: {k.get('status', '?')}\n\n"
                )
        else:
            text += "Ключей не найдено.\n"
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🔙 Назад", callback_data="admin_back"))
        self.bot.edit_message_text(
            text, chat_id, message_id,
            reply_markup=markup, parse_mode="HTML",
        )
        self.bot.answer_callback_query(call.id if hasattr(call, 'id') else None)