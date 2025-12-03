import json
import boto3

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("Inventory")


def lambda_handler(event, context):
    """
    DELETE /item/{id}?location_id=1

    Path parameter:
      - id : item_id

    Query string:
      - location_id : item_location_id
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

        # First check if the item exists
        existing = table.get_item(
            Key={"item_id": item_id, "item_location_id": location_id}
        ).get("Item")

        if not existing:
            return {
                "statusCode": 404,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"message": "Item not found"}),
            }

        table.delete_item(Key={"item_id": item_id, "item_location_id": location_id})

        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"message": "Item deleted successfully"}),
        }

    except Exception as e:
        print(f"Error in delete_inventory_item: {e}")
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps(
                {"message": "Error deleting inventory item", "error": str(e)}
            ),
        }
