import boto3
import json
import json
import traceback


region = boto3.session.Session().region_name

def lambda_handler(event, context):
    print(f"Event is: {event}")

    response = 'This function is not ready, please complete the next two tasks and test again.'
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
            
