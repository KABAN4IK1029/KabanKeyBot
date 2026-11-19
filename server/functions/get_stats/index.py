# -*- coding: utf-8 -*-
"""Lambda: статистика системы."""
import json
import os
import boto3

dynamodb = boto3.resource("dynamodb")
TABLE_KEYS = os.environ.get("TABLE_KEYS", "kaban_keys")
TABLE_USERS = os.environ.get("TABLE_USERS", "kaban_users")


def lambda_handler(event, context):
    try:
        table_keys = dynamodb.Table(TABLE_KEYS)
        table_users = dynamodb.Table(TABLE_USERS)

        total = table_keys.scan(Select="COUNT").get("Count", 0)
        unused = table_keys.scan(
            FilterExpression="#st = :st",
            ExpressionAttributeNames={"#st": "status"},
            ExpressionAttributeValues={":st": "unused"},
            Select="COUNT",
        ).get("Count", 0)
        active = table_keys.scan(
            FilterExpression="#st = :st",
            ExpressionAttributeNames={"#st": "status"},
            ExpressionAttributeValues={":st": "active"},
            Select="COUNT",
        ).get("Count", 0)
        admins = table_users.scan(
            FilterExpression="is_admin = :val",
            ExpressionAttributeValues={":val": True},
            Select="COUNT",
        ).get("Count", 0)

        return _response(200, {
            "success": True,
            "total_keys": total,
            "unused_keys": unused,
            "active_keys": active,
            "admin_count": admins,
        })
    except Exception as e:
        return _response(500, {"success": False, "error": str(e)})


def _response(code, data):
    return {
        "statusCode": code,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(data),
    }