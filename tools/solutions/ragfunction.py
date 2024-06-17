import os
import json
import boto3
from langchain_community.retrievers import AmazonKendraRetriever
from langchain_aws import ChatBedrock
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate

import traceback

kendra = boto3.client('kendra')

KENDRA_INDEX_ID = os.getenv('KENDRA_INDEX_ID')
S3_BUCKET_NAME = os.environ["S3_BUCKET_NAME"]


def lambda_handler(event, context):
    print(f"Event is: {event}")
    
    event_body = json.loads(event["body"])
    question = event_body["query"]
    print(f"Query is: {question}")
    
    model_id = event_body["model_id"]
    temperature = event_body["temperature"]
    max_tokens = event_body["max_tokens"]

    response = ''
    status_code = 200

    PROMPT_TEMPLATE = 'prompt-engineering/claude-prompt-template.txt'

    try:
        if model_id == 'mistral.mistral-7b-instruct-v0:2':
            llm = get_mistral_llm(model_id,temperature,max_tokens)
            PROMPT_TEMPLATE = 'prompt-engineering/mistral-prompt-template.txt'
        elif model_id == 'meta.llama2-13b-chat-v1':
            llm = get_llama_llm(model_id,temperature,max_tokens)
            PROMPT_TEMPLATE = 'prompt-engineering/llama-prompt-template.txt'
        else:
            llm = get_claude_llm(model_id,temperature,max_tokens)
            PROMPT_TEMPLATE = 'prompt-engineering/claude-prompt-template.txt'
        
        # Read the prompt template from S3 bucket
        s3 = boto3.resource('s3')
        obj = s3.Object(S3_BUCKET_NAME, PROMPT_TEMPLATE) 
        prompt_template = obj.get()['Body'].read().decode('utf-8')
        print(f"prompt template: {prompt_template}")
            
        PROMPT = PromptTemplate(
            template=prompt_template, input_variables=["context", "question"]
        )
            
        # Initialize the Kendra loader
        retriever = AmazonKendraRetriever(
            kendra_client=kendra,
            index_id=KENDRA_INDEX_ID
        )
        conversation_with_retrieval = ConversationalRetrievalChain.from_llm(llm, retriever, memory=get_memory(), return_source_documents=True, verbose=False)
        
        chat_response = conversation_with_retrieval.invoke({"question": question, "prompt": PROMPT})
        print(f"chat_response is: {chat_response}")
        
        previous_source = None
        previous_score = None
        response_data = []
        for source_doc in chat_response["source_documents"]:
            source = source_doc.metadata["source"]
            score = source_doc.metadata["score"]
            excerpt_page_number = source_doc.metadata.get("document_attributes", {}).get("_excerpt_page_number", "N/A")
        
            if source != previous_source or score != previous_score:
                source_data = {
                    "source": source,
                    "score": score,
                    "excerpt_page_number": excerpt_page_number
                }
                response_data.append(source_data)
                previous_source = source
                previous_score = score
        
        response_with_metadata = {
            "answer": chat_response['answer'],
            "source_documents": response_data
        }
        
        print(f"Response with metadata: {response_with_metadata}")
            
        return {
            'statusCode': status_code,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                'Access-Control-Allow-Methods': 'OPTIONS,POST'
            },
            'body': json.dumps(response_with_metadata)
            
        }

    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")
        stack_trace = traceback.format_exc()
        print(f"stack trace: {stack_trace}")
        print(f"error: {str(e)}")
        
        response = str(e)
        return {
            'statusCode': status_code,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                'Access-Control-Allow-Methods': 'OPTIONS,POST'
            },
            'body': json.dumps({'error': response})
        }
        
def get_claude_llm(model_id, temperature, max_tokens):
    model_kwargs = {
        "max_tokens": max_tokens,
        "temperature": temperature, 
        "top_k": 50, 
        "top_p": 1
    }
    llm = ChatBedrock(model_id=model_id, model_kwargs=model_kwargs) 
    return llm

def get_llama_llm(model_id, temperature, max_tokens):
    model_kwargs = {
        "max_gen_len": max_tokens,
        "temperature": temperature, 
        "top_p": 0.7
    }
    llm = ChatBedrock(model_id=model_id, model_kwargs=model_kwargs) 
    return llm

def get_mistral_llm(model_id, temperature, max_tokens):
    model_kwargs = { 
        "max_tokens": max_tokens,
        "temperature": temperature, 
        "top_k": 50, 
        "top_p": 0.7
    }
    llm = ChatBedrock(model_id=model_id, model_kwargs=model_kwargs) 
    return llm

def get_memory():
 
    memory = ConversationBufferMemory(
        memory_key="chat_history",
        input_key="question",
        output_key="answer",
        return_messages=True
    )
    return memory
