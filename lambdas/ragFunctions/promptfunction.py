import os
import json
import boto3
from langchain_community.retrievers import AmazonKendraRetriever
from langchain_aws import ChatBedrockConverse
from langchain_core.messages import HumanMessage
import traceback

# Set up the Kendra client
kendra = boto3.client('kendra')

KENDRA_INDEX_ID = os.getenv('KENDRA_INDEX_ID')

def lambda_handler(event, context):
    print(f"Event is: {event}")
    
    event_body = json.loads(event["body"])
    question = event_body["query"]
    prompt_template = event_body["prompt"]
    print(f"Query: {question}")
    print(f"Prompt: {prompt_template}")
    
    model_id = event_body["model_id"]
    temperature = event_body["temperature"]
    max_tokens = event_body["max_tokens"]

    status_code = 200
    
    try:
        llm = ChatBedrockConverse(
            model=model_id,
            temperature=temperature,
            max_tokens=max_tokens
        )

        # Retrieve relevant documents from Kendra
        retriever = AmazonKendraRetriever(
            kendra_client=kendra,
            index_id=KENDRA_INDEX_ID
        )
        docs = retriever.get_relevant_documents(question)
        context_text = "\n\n".join(doc.page_content for doc in docs)

        # Build the final prompt by substituting context and question
        final_prompt = prompt_template.replace("{context}", context_text).replace("{question}", question)
        print(f"Final prompt length: {len(final_prompt)}")

        # Invoke the model directly
        result = llm.invoke([HumanMessage(content=final_prompt)])
        answer = result.content
        print(f"Response: {answer}")
        
        return {
            'statusCode': status_code,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                'Access-Control-Allow-Methods': 'OPTIONS,POST'
            },
            'body': json.dumps({'answer': answer})
        }

    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")
        stack_trace = traceback.format_exc()
        print(f"stack trace: {stack_trace}")
        
        return {
            'statusCode': status_code,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                'Access-Control-Allow-Methods': 'OPTIONS,POST'
            },
            'body': json.dumps({'error': str(e)})
        }
