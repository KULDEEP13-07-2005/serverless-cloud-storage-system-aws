import boto3

s3 = boto3.client('s3')
BUCKET = "scssuaws28042026"

def lambda_handler(event, context):
    url = s3.generate_presigned_url(
        'get_object',
        Params={'Bucket': BUCKET, 'Key': event['s3Key']},
        ExpiresIn=60
    )
    return {"downloadURL": url}