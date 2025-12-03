import json
import boto3
from decimal import Decimal

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("InventoryApp")


def decimal_to_float(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError


def lambda_handler(event, context):
    """
    GET /item/{id}?location_id=1

    Path parameter:
      - id : item_id (string)

    Query string:
      - location_id : item_location_id (number)

    Returns a single item or 404 if not found.
    """
    try:
        path_params = event.get("pathParameters") or {}
        query_params = event.get("queryStringParameters") or {}

        item_id = path_params.get("id")
        location_id_str = query_params.get("location_id") if query_params else None

        if not item_id or location_id_str is None:
            return {
                "statusCode": 400,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps(
                    {
                        "message": "Missing required parameters: id (path) and location_id (query string)."
                    }
                ),
            }

        location_id = int(location_id_str)

        response = table.get_item(
            Key={"item_id": item_id, "item_location_id": location_id}
        )

        item = response.get("Item")
        if not item:
            return {
                "statusCode": 404,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"message": "Item not found"}),
            }

        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps(item, default=decimal_to_float),
        }

    except Exception as e:
        print(f"Error in get_inventory_item: {e}")
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps(
                {"message": "Error fetching inventory item", "error": str(e)}
            ),
        }
