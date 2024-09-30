import boto3
import json


region = boto3.session.Session().region_name

def lambda_handler(event, context):
    print(f"Event is: {event}")

    response = 'This function is not yet available. Please proceed to Task 8, where you will implement it.'
    status_code = 200
    

    return {
        'statusCode': status_code,
        'headers': {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
            'Access-Control-Allow-Methods': 'OPTIONS,POST'
        },
        'body': json.dumps({'answer': response})
    }
            
