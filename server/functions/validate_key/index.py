# -*- coding: utf-8 -*-
"""Lambda: проверка ключа."""
import json
import os
import boto3

dynamodb = boto3.resource("dynamodb")
TABLE_KEYS = os.environ.get("TABLE_KEYS", "kaban_keys")


def lambda_handler(event, context):
    try:
        body = json.loads(event.get("body", "{}")) if isinstance(event.get("body"), str) else event
        key_value = body.get("key", "").strip().upper()

        table = dynamodb.Table(TABLE_KEYS)
        resp = table.get_item(Key={"key": key_value})
        item = resp.get("Item")

        if not item:
            return _response(404, {"success": False, "error": "Ключ не найден"})

        return _response(200, {
            "success": True,
            "key": item.get("key"),
            "status": item.get("status"),
            "prefix": item.get("prefix"),
            "created_by": item.get("created_by"),
            "activated_by": item.get("activated_by"),
        })
    except Exception as e:
        return _response(500, {"success": False, "error": str(e)})


def _response(code, data):
    return {
        "statusCode": code,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(data),
    }