import json
import boto3
from decimal import Decimal

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("Inventory")


def decimal_to_float(obj):
    """Helper for json.dumps so it can serialize Decimal."""
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError


def lambda_handler(event, context):
    """
    GET /item
    Return all inventory items in the table.
    """
    try:
        response = table.scan()
        items = response.get("Items", [])

        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps(items, default=decimal_to_float),
        }

    except Exception as e:
        # Log error (CloudWatch)
        print(f"Error in get_all_inventory_items: {e}")

        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps(
                {"message": "Error fetching inventory items", "error": str(e)}
            ),
        }
