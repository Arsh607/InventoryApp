import json
import boto3
from decimal import Decimal
from uuid import uuid4

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("InventoryApp")


def lambda_handler(event, context):
    """
    POST /item
    Body JSON example:
    {
      "item_location_id": 1,
      "item_name": "Camping Chair",
      "item_description": "Lightweight folding camping chair with cup holder.",
      "item_qty_on_hand": 25,
      "item_price": 49.99
    }
    """
    try:
        if not event.get("body"):
            return {
                "statusCode": 400,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"message": "Request body is required."}),
            }

        body = json.loads(event["body"])

        # Validate required fields
        required_fields = [
            "item_location_id",
            "item_name",
            "item_description",
            "item_qty_on_hand",
            "item_price",
        ]
        missing = [f for f in required_fields if f not in body]
        if missing:
            return {
                "statusCode": 400,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps(
                    {"message": f"Missing required fields: {', '.join(missing)}"}
                ),
            }

        item_location_id = int(body["item_location_id"])
        item_qty_on_hand = int(body["item_qty_on_hand"])
        item_price = float(body["item_price"])

        # Generate a unique item_id (ULID-like string; uuid4 is fine for this project)
        item_id = str(uuid4())

        item = {
            "item_id": item_id,
            "item_location_id": item_location_id,
            "item_name": body["item_name"],
            "item_description": body["item_description"],
            "item_qty_on_hand": item_qty_on_hand,
            "item_price": Decimal(str(item_price)),
        }

        table.put_item(Item=item)

        # Convert Decimal back to float for the response
        item["item_price"] = float(item["item_price"])

        return {
            "statusCode": 201,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps(item),
        }

    except Exception as e:
        print(f"Error in add_inventory_item: {e}")
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps(
                {"message": "Error adding inventory item", "error": str(e)}
            ),
        }
