import boto3, uuid

s3 = boto3.client('s3')
BUCKET = "bucket_name"

def lambda_handler(event, context):
    file_name = event['fileName']
    file_id = str(uuid.uuid4())
    s3_key = f"uploads/{file_id}_{file_name}"

    url = s3.generate_presigned_url(
        'put_object',
        Params={'Bucket': BUCKET, 'Key': s3_key},
        ExpiresIn=300
    )

    return {
        "fileId": file_id,
        "uploadURL": url,
        "s3Key": s3_key
    }
