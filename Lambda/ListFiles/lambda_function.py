import json
import boto3

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('FileMetadata')

s3 = boto3.client('s3')
BUCKET = "bucket_name"

def lambda_handler(event, context):
    try:
        files = []

        # 🔹 Step 1: Get from DynamoDB
        db_response = table.scan()

        db_files = db_response.get("Items", [])

        # Convert to dictionary for quick lookup
        db_map = {item["s3Key"]: item for item in db_files}

        # 🔹 Step 2: Get from S3
        s3_response = s3.list_objects_v2(
            Bucket=BUCKET,
            Prefix="uploads/"
        )

        s3_files = s3_response.get("Contents", [])

        for obj in s3_files:
            key = obj["Key"]

            if key.endswith("/"):
                continue  # skip folders

            # 🔹 Step 3: Check if metadata exists
            if key in db_map:
                files.append({
                    "fileId": db_map[key]["fileId"],
                    "fileName": db_map[key]["fileName"],
                    "s3Key": key
                })
            else:
                # 🔥 File exists in S3 but not in DynamoDB
                import uuid

                new_id = str(uuid.uuid4())

                # Save to DynamoDB
                table.put_item(
                    Item={
                        "fileId": new_id,
                        "fileName": key.split("/")[-1],
                        "s3Key": key
                    }
                )

                files.append({
                    "fileId": new_id,
                    "fileName": key.split("/")[-1],
                    "s3Key": key
                })

        return {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps({
                "files": files
            })
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": str(e)
        }
