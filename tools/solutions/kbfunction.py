import os
import json
import boto3

import traceback


KB_ID = os.environ["KB_ID"]


def lambda_handler(event, context):
    boto3_version = boto3.__version__
    print(f"Boto3 version: {boto3_version}")
    
    print(f"Event is: {event}")
    event_body = json.loads(event["body"])
    prompt = event_body["query"]
    model_id = event_body["model_id"]
    
    response = ''
    status_code = 200
    
    try:
        print(f"Model id: {model_id}")
        
        # Step 1: Retrieve relevant passages from the knowledge base
        passages = retrieve_from_kb(prompt)
        
        # Step 2: Generate a response using the Converse API (supports inference profile IDs)
        response = generate_with_converse(prompt, passages, model_id)
        
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


def retrieve_from_kb(query, max_results=5):
    """Retrieve relevant passages from the knowledge base."""
    bedrock_agent_runtime = boto3.client(service_name="bedrock-agent-runtime")
    
    response = bedrock_agent_runtime.retrieve(
        knowledgeBaseId=KB_ID,
        retrievalQuery={'text': query},
        retrievalConfiguration={
            'vectorSearchConfiguration': {
                'numberOfResults': max_results
            }
        }
    )
    
    passages = []
    for result in response.get('retrievalResults', []):
        text = result.get('content', {}).get('text', '')
        if text:
            passages.append(text)
    
    print(f"Retrieved {len(passages)} passages from KB")
    return passages


def generate_with_converse(query, passages, model_id):
    """Generate a response using the Converse API with retrieved context.
    
    The Converse API accepts inference profile IDs (us.*, eu.*, ap.*)
    directly in the modelId field, avoiding the GetInferenceProfile
    permission issue that RetrieveAndGenerate has.
    """
    bedrock_runtime = boto3.client(service_name="bedrock-runtime")
    
    # Build context from retrieved passages
    context = "\n\n---\n\n".join(passages)
    
    prompt_with_context = (
        f"Answer the following question based on the provided context. "
        f"If the context doesn't contain enough information to answer, say so.\n\n"
        f"Context:\n{context}\n\n"
        f"Question: {query}"
    )
    
    response = bedrock_runtime.converse(
        modelId=model_id,
        messages=[
            {
                'role': 'user',
                'content': [{'text': prompt_with_context}]
            }
        ],
        inferenceConfig={
            'maxTokens': 2048,
            'temperature': 0.7
        }
    )
    
    output = response['output']['message']['content'][0]['text']
    print(f"Generated response length: {len(output)}")
    return output
