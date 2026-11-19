# -*- coding: utf-8 -*-
"""Lambda: активация ключа для пользователя."""
import json
import os
import time
import boto3
from botocore.exceptions import ClientError

dynamodb = boto3.resource("dynamodb")
TABLE_KEYS = os.environ.get("TABLE_KEYS", "kaban_keys")
TABLE_USERS = os.environ.get("TABLE_USERS", "kaban_users")


def lambda_handler(event, context):
    try:
        body = json.loads(event.get("body", "{}")) if isinstance(event.get("body"), str) else event
        key_value = body.get("key", "").strip().upper()
        user_id = str(body.get("user_id", ""))
        username = body.get("username", "")

        if not key_value or not user_id:
            return _response(400, {"success": False, "error": "Необходимы key и user_id"})

        table_keys = dynamodb.Table(TABLE_KEYS)

        try:
            table_keys.update_item(
                Key={"key": key_value},
                UpdateExpression="SET #st = :st, activated_by = :ub, activated_at = :at",
                ExpressionAttributeNames={"#st": "status"},
                ExpressionAttributeValues={":st": "active", ":ub": user_id, ":at": int(time.time()), ":unused": "unused"},
                ConditionExpression="#st = :unused",
            )
        except ClientError as e:
            if e.response["Error"]["Code"] == "ConditionalCheckFailedException":
                return _response(409, {"success": False, "error": "Ключ уже активирован"})
            raise

        # Обновляем статистику пользователя
        table_users = dynamodb.Table(TABLE_USERS)
        try:
            table_users.update_item(
                Key={"user_id": user_id},
                UpdateExpression="SET keys_activated = if_not_exists(keys_activated, :zero) + :inc",
                ExpressionAttributeValues={":zero": 0, ":inc": 1},
            )
        except Exception:
            pass

        return _response(200, {"success": True, "key": key_value})
    except Exception as e:
        return _response(500, {"success": False, "error": str(e)})


def _response(code, data):
    return {
        "statusCode": code,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(data),
    }