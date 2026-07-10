import json
import boto3

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('FileMetadata')  # replace

def lambda_handler(event, context):
    try:
        print("EVENT:", event)

        # Case 1: body exists
        if "body" in event and event["body"]:
            if isinstance(event["body"], str):
                body = json.loads(event["body"])
            else:
                body = event["body"]

        # Case 2: direct payload (no body)
        else:
            body = event

        fileId = body.get("fileId")
        fileName = body.get("fileName")
        s3Key = body.get("s3Key")

        if not fileId or not fileName or not s3Key:
            raise Exception("Missing required fields")

        table.put_item(
            Item={
                "fileId": fileId,
                "fileName": fileName,
                "s3Key": s3Key
            }
        )

        return {
            "statusCode": 200,
            "headers": {"Access-Control-Allow-Origin": "*"},
            "body": json.dumps({"message": "Saved successfully"})
        }

    except Exception as e:
        print("ERROR:", str(e))

        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
