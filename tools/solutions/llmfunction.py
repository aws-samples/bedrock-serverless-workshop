import boto3
import json
import traceback


region = boto3.session.Session().region_name

def lambda_handler(event, context):
    boto3_version = boto3.__version__
    print(f"Boto3 version: {boto3_version}")
    
    print(f"Event is: {event}")
    event_body = json.loads(event["body"])
    prompt = event_body["query"]
    temperature = event_body["temperature"]
    max_tokens = event_body["max_tokens"]
    model_id = event_body["model_id"]
    
    response = ''
    status_code = 200
    
    try:
        if 'anthropic' in model_id:
            response = invoke_claude(model_id, prompt, temperature, max_tokens)
        elif 'amazon.nova' in model_id:
            response = invoke_nova(model_id, prompt, temperature, max_tokens)
        elif 'meta' in model_id:
            response = invoke_llama(model_id, prompt, temperature, max_tokens)
        elif 'mistral' in model_id:
            response = invoke_mistral(model_id, prompt, temperature, max_tokens)
        else:
            response = invoke_claude(model_id, prompt, temperature, max_tokens)
            
        return {
            'statusCode': status_code,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                'Access-Control-Allow-Methods': 'OPTIONS,POST'
            },
            'body': json.dumps({'answer': response})
        }
            
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")
        stack_trace = traceback.format_exc()
        print(stack_trace)
        return {
            'statusCode': status_code,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                'Access-Control-Allow-Methods': 'OPTIONS,POST'
            },
            'body': json.dumps({'error': str(e)})
        }


def invoke_claude(model_id, prompt, temperature, max_tokens):
    try:

        instruction = f"Human: {prompt} nAssistant:"
        bedrock_runtime_client = boto3.client(service_name="bedrock-runtime", region_name=region)
        body= {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": max_tokens,
                "messages": [
                    {
                        "role": "user",
                        "content": [{"type": "text", "text": prompt}],
                    }
                ],
        }

        response = bedrock_runtime_client.invoke_model(
            modelId=model_id, body=json.dumps(body)
        )

        response_body = json.loads(response["body"].read())
        outputs = response_body.get("content")
        completions = [output["text"] for output in outputs]
        print(f"completions: {completions[0]}")

        return completions[0]

    except Exception as e:
        raise
        
def invoke_nova(model_id, prompt, temperature, max_tokens):
    print(f"Invoking Nova model {model_id}")
    try:
        bedrock_runtime_client = boto3.client(service_name="bedrock-runtime", region_name=region)
        body = {
            "messages": [
                {
                    "role": "user",
                    "content": [{"text": prompt}],
                }
            ],
            "inferenceConfig": {
                "maxTokens": max_tokens,
                "temperature": temperature,
                "topP": 0.9
            }
        }

        response = bedrock_runtime_client.invoke_model(
            modelId=model_id, body=json.dumps(body)
        )
        response_body = json.loads(response["body"].read())
        output_message = response_body.get("output", {}).get("message", {})
        completions = [block["text"] for block in output_message.get("content", [])]
        print(f"completions: {completions[0]}")
        return completions[0]
    except Exception as e:
        raise

def invoke_mistral(model_id, prompt, temperature, max_tokens):
    print(f"Invoking Mistral model {model_id}")
    try:
        bedrock_runtime_client = boto3.client(service_name="bedrock-runtime", region_name=region)
        body = {
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "max_tokens": max_tokens,
            "temperature": temperature,
        }

        response = bedrock_runtime_client.invoke_model(
            modelId=model_id, body=json.dumps(body)
        )
        response_body = json.loads(response["body"].read())
        choices = response_body.get("choices", [])
        print(f"response: {choices}")
        return choices[0]["message"]["content"]
    except Exception as e:
        raise
        
def invoke_llama(model_id, prompt, temperature, max_tokens):
    print(f"Invoking Llama model {model_id}")
    try:
        bedrock_runtime_client = boto3.client(service_name="bedrock-runtime", region_name=region)
        
        body = {
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "max_tokens": max_tokens,
            "temperature": temperature,
            "top_p": 0.9
        }

        response = bedrock_runtime_client.invoke_model(
            modelId=model_id, body=json.dumps(body)
        )
        response_body = json.loads(response["body"].read())
        print(f"response: {response_body}")
        choices = response_body.get("choices", [])
        return choices[0]["message"]["content"]
    except Exception as e:
        raise
