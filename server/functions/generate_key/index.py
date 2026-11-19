# -*- coding: utf-8 -*-
"""Lambda: генерация нового ключа."""
import json
import os
import random
import string
import boto3
from botocore.exceptions import ClientError

dynamodb = boto3.resource("dynamodb")
TABLE_KEYS = os.environ.get("TABLE_KEYS", "kaban_keys")
TABLE_SETTINGS = os.environ.get("TABLE_SETTINGS", "kaban_settings")


def generate_suffix(length=4):
    chars = string.ascii_uppercase + string.digits
    return "".join(random.choice(chars) for _ in range(length))


def lambda_handler(event, context):
    try:
        body = json.loads(event.get("body", "{}")) if isinstance(event.get("body"), str) else event
        prefix = body.get("prefix") or get_default_prefix()
        created_by = body.get("created_by", "admin")

        key = f"{prefix}-{generate_suffix(4)}-{generate_suffix(4)}-{generate_suffix(4)}"

        table = dynamodb.Table(TABLE_KEYS)
        table.put_item(
            Item={
                "key": key,
                "prefix": prefix,
                "status": "unused",
                "created_by": str(created_by),
                "created_by_username": body.get("created_by_username", ""),
                "created_at": int(__import__("time").time()),
                "activated_by": "",
                "activated_at": 0,
            }
        )

        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"success": True, "key": key, "prefix": prefix}),
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"success": False, "error": str(e)}),
        }


def get_default_prefix():
    try:
        table = dynamodb.Table(TABLE_SETTINGS)
        resp = table.get_item(Key={"setting_key": "key_prefix"})
        item = resp.get("Item")
        if item:
            return item.get("setting_value", "KABAN4IK1029")
    except Exception:
        pass
    return "KABAN4IK1029"