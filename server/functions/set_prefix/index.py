# -*- coding: utf-8 -*-
"""Lambda: смена префикса ключей (только админ)."""
import json
import os
import boto3

dynamodb = boto3.resource("dynamodb")
TABLE_SETTINGS = os.environ.get("TABLE_SETTINGS", "kaban_settings")


def lambda_handler(event, context):
    try:
        body = json.loads(event.get("body", "{}")) if isinstance(event.get("body"), str) else event
        prefix = body.get("prefix", "").strip()
        user_id = body.get("user_id", "")

        if not prefix or "-" in prefix or " " in prefix:
            return _response(400, {"success": False, "error": "Неверный префикс"})

        table = dynamodb.Table(TABLE_SETTINGS)
        table.put_item(Item={"setting_key": "key_prefix", "setting_value": prefix})

        return _response(200, {"success": True, "prefix": prefix})
    except Exception as e:
        return _response(500, {"success": False, "error": str(e)})


def _response(code, data):
    return {
        "statusCode": code,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(data),
    }