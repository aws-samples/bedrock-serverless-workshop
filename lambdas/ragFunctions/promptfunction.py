import os
import json
import boto3
from langchain_community.retrievers import AmazonKendraRetriever
from langchain_aws import ChatBedrock
from langchain.memory import ConversationBufferWindowMemory
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
import traceback

# Set up the Bedrock client
bedrock = boto3.client('bedrock')

# Set up the Kendra client
kendra = boto3.client('kendra')

KENDRA_INDEX_ID = os.getenv('KENDRA_INDEX_ID')
S3_BUCKET_NAME = os.environ["S3_BUCKET_NAME"]


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

    response = ''
    status_code = 200
    
    try:
        llm = get_claude_llm(model_id, temperature, max_tokens)

        # Initialize the Kendra loader
        retriever = AmazonKendraRetriever(
            kendra_client=kendra,
            index_id=KENDRA_INDEX_ID
        )
        #PROMPT_TEMPLATE = 'prompt-engineering/claude-prompt-template.txt'
        #s3 = boto3.resource('s3')
        #obj = s3.Object(S3_BUCKET_NAME, PROMPT_TEMPLATE) 
        #prompt_template = obj.get()['Body'].read().decode('utf-8')
        #print(f"prompt: {prompt_template}")
        
        claude_prompt = PromptTemplate(
                template=prompt_template, input_variables=["context","question"]
        )
        
        qa = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=retriever,
            return_source_documents=False,
            chain_type_kwargs={"prompt": claude_prompt}
        )
        
        #response = qa.invoke(question)
        response = qa(question, return_only_outputs=True)
        print(response)
        
        response_with_metadata = {
            "answer": response['result']
        }
        
            
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

#This is a TODO item, presently the history is not retained between the calls
def get_memory(): 
    memory = ConversationBufferWindowMemory(
                    memory_key="chat_history", 
                    k=5,
                    input_key="question",
                    output_key="answer",
                    return_messages=True) 
    return memory
