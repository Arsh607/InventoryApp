import json
import boto3
from decimal import Decimal
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("InventoryApp")

GSI_NAME = "GSI1_LocationItem"  # change if you used a different name


def decimal_to_float(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError


def lambda_handler(event, context):
    """
    GET /location/{id}

    Path parameter:
      - id : item_location_id (number)

    Returns all items for that location (using the GSI).
    """
    try:
        path_params = event.get("pathParameters") or {}
        location_id_str = path_params.get("id")

        if location_id_str is None:
            return {
                "statusCode": 400,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps(
                    {"message": "Missing required path parameter: id (location_id)."}
                ),
            }

        location_id = int(location_id_str)

        response = table.query(
            IndexName=GSI_NAME,
            KeyConditionExpression=Key("item_location_id").eq(location_id),
        )
        items = response.get("Items", [])

        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps(items, default=decimal_to_float),
        }

    except Exception as e:
        print(f"Error in get_location_inventory_items: {e}")
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps(
                {
                    "message": "Error fetching items for location",
                    "error": str(e),
                }
            ),
        }
