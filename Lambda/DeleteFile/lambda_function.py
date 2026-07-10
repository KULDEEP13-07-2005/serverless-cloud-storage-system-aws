import json
import boto3

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('FileMetadata')

s3 = boto3.client('s3')
BUCKET = "bucket_name"

def lambda_handler(event, context):
    try:
        print("EVENT:", event)

        # 🔥 Handle all cases safely
        if "body" in event and event["body"]:
            if isinstance(event["body"], str):
                body = json.loads(event["body"])
            else:
                body = event["body"]
        else:
            body = event  # direct payload case

        file_id = body.get("fileId")

        if not file_id:
            raise Exception("fileId missing")

        # 🔹 Get item
        response = table.get_item(
            Key={"fileId": file_id}
        )

        if "Item" not in response:
            return {
                "statusCode": 404,
                "body": json.dumps({"message": "File not found"})
            }

        s3_key = response["Item"].get("s3Key")

        # 🔹 Delete from S3
        if s3_key:
            s3.delete_object(
                Bucket=BUCKET,
                Key=s3_key
            )

        # 🔹 Delete from DynamoDB
        table.delete_item(
            Key={"fileId": file_id}
        )

        return {
            "statusCode": 200,
            "headers": {"Access-Control-Allow-Origin": "*"},
            "body": json.dumps({"message": "Deleted successfully"})
        }

    except Exception as e:
        print("ERROR:", str(e))

        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
