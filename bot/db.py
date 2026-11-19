# -*- coding: utf-8 -*-
"""Работа с DynamoDB."""
import time
import boto3
from botocore.exceptions import ClientError
from config import (
    AWS_REGION, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY,
    TABLE_KEYS, TABLE_USERS, TABLE_SETTINGS,
)


class DynamoDBClient:
    def __init__(self):
        self.region = AWS_REGION
        self.access_key = AWS_ACCESS_KEY_ID
        self.secret_key = AWS_SECRET_ACCESS_KEY
        self._dynamodb = None

    @property
    def dynamodb(self):
        if self._dynamodb is None:
            kwargs = {"region_name": self.region}
            if self.access_key and self.secret_key:
                kwargs["aws_access_key_id"] = self.access_key
                kwargs["aws_secret_access_key"] = self.secret_key
            self._dynamodb = boto3.resource("dynamodb", **kwargs)
        return self._dynamodb

    # ---------- Ключи ----------
    def get_key(self, key_value):
        """Получить информацию о ключе по его значению."""
        table = self.dynamodb.Table(TABLE_KEYS)
        try:
            resp = table.get_item(Key={"key": key_value})
            return resp.get("Item")
        except ClientError as e:
            print(f"[DB] Ошибка получения ключа: {e}")
            return None

    def create_key(self, key_value, prefix, created_by, created_by_username=None):
        """Создать новый ключ в базе."""
        table = self.dynamodb.Table(TABLE_KEYS)
        item = {
            "key": key_value,
            "prefix": prefix,
            "status": "unused",
            "created_by": str(created_by),
            "created_by_username": created_by_username or "",
            "created_at": int(time.time()),
            "activated_by": "",
            "activated_at": 0,
        }
        try:
            table.put_item(Item=item)
            return True
        except ClientError as e:
            print(f"[DB] Ошибка создания ключа: {e}")
            return False

    def activate_key(self, key_value, user_id, username):
        """Активировать ключ для пользователя."""
        table = self.dynamodb.Table(TABLE_KEYS)
        try:
            table.update_item(
                Key={"key": key_value},
                UpdateExpression="SET #st = :st, activated_by = :ub, activated_at = :at",
                ExpressionAttributeNames={"#st": "status"},
                ExpressionAttributeValues={":st": "active", ":ub": str(user_id), ":at": int(time.time()), ":unused": "unused"},
                ConditionExpression="#st = :unused",
            )
            self._increment_user_stat(user_id, username, "keys_activated")
            return True
        except ClientError as e:
            if e.response["Error"]["Code"] == "ConditionalCheckFailedException":
                print(f"[DB] Ключ уже активирован: {key_value}")
                return False
            print(f"[DB] Ошибка активации ключа: {e}")
            return False

    def list_keys(self, limit=50, status=None):
        """Список ключей (для админа)."""
        table = self.dynamodb.Table(TABLE_KEYS)
        try:
            if status:
                resp = table.scan(
                    FilterExpression="#st = :st",
                    ExpressionAttributeNames={"#st": "status"},
                    ExpressionAttributeValues={":st": status},
                    Limit=limit,
                )
            else:
                resp = table.scan(Limit=limit)
            return resp.get("Items", [])
        except ClientError as e:
            print(f"[DB] Ошибка получения списка ключей: {e}")
            return []

    def count_keys(self, status=None):
        """Подсчет ключей по статусу."""
        table = self.dynamodb.Table(TABLE_KEYS)
        try:
            if status:
                resp = table.scan(
                    FilterExpression="#st = :st",
                    ExpressionAttributeNames={"#st": "status"},
                    ExpressionAttributeValues={":st": status},
                    Select="COUNT",
                )
            else:
                resp = table.scan(Select="COUNT")
            return resp.get("Count", 0)
        except ClientError:
            return 0

    # ---------- Пользователи ----------
    def get_user(self, user_id):
        """Получить пользователя по ID."""
        table = self.dynamodb.Table(TABLE_USERS)
        try:
            resp = table.get_item(Key={"user_id": str(user_id)})
            return resp.get("Item")
        except ClientError as e:
            print(f"[DB] Ошибка получения пользователя: {e}")
            return None

    def create_user(self, user_id, username, is_admin=False):
        """Создать пользователя."""
        table = self.dynamodb.Table(TABLE_USERS)
        item = {
            "user_id": str(user_id),
            "username": username or "",
            "is_admin": is_admin,
            "created_at": int(time.time()),
            "keys_generated": 0,
            "keys_activated": 0,
        }
        try:
            table.put_item(Item=item)
            return item
        except ClientError as e:
            print(f"[DB] Ошибка создания пользователя: {e}")
            return None

    def is_admin(self, user_id):
        """Проверка, является ли пользователь админом."""
        user = self.get_user(user_id)
        if user:
            return user.get("is_admin", False)
        return False

    def set_admin(self, user_id, is_admin=True):
        """Установить статус админа."""
        table = self.dynamodb.Table(TABLE_USERS)
        try:
            table.update_item(
                Key={"user_id": str(user_id)},
                UpdateExpression="SET is_admin = :admin",
                ExpressionAttributeValues={":admin": is_admin},
            )
            return True
        except ClientError as e:
            print(f"[DB] Ошибка установки админа: {e}")
            return False

    def list_admins(self):
        """Список всех админов."""
        table = self.dynamodb.Table(TABLE_USERS)
        try:
            resp = table.scan(
                FilterExpression="is_admin = :val",
                ExpressionAttributeValues={":val": True},
            )
            return resp.get("Items", [])
        except ClientError:
            return []

    def _increment_user_stat(self, user_id, username, stat_field):
        """Увеличить статистику пользователя."""
        table = self.dynamodb.Table(TABLE_USERS)
        try:
            table.update_item(
                Key={"user_id": str(user_id)},
                UpdateExpression=f"SET {stat_field} = if_not_exists({stat_field}, :zero) + :inc",
                ExpressionAttributeValues={":zero": 0, ":inc": 1},
            )
        except ClientError:
            pass

    # ---------- Настройки ----------
    def get_setting(self, key, default=None):
        """Получить настройку."""
        table = self.dynamodb.Table(TABLE_SETTINGS)
        try:
            resp = table.get_item(Key={"setting_key": key})
            item = resp.get("Item")
            return item.get("setting_value") if item else default
        except ClientError:
            return default

    def set_setting(self, key, value):
        """Установить настройку."""
        table = self.dynamodb.Table(TABLE_SETTINGS)
        try:
            table.put_item(Item={"setting_key": key, "setting_value": value})
            return True
        except ClientError as e:
            print(f"[DB] Ошибка сохранения настройки: {e}")
            return False

    def get_key_prefix(self):
        """Получить текущий префикс ключей."""
        prefix = self.get_setting("key_prefix")
        return prefix if prefix else "KABAN4IK1029"

    def set_key_prefix(self, prefix):
        """Установить префикс ключей (только админ)."""
        return self.set_setting("key_prefix", prefix)