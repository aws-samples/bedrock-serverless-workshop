import traceback
import json
import boto3 
import os
from langchain.llms.bedrock import Bedrock
from langchain import PromptTemplate
from typing import Optional, List, Mapping, Any, Dict
from langchain.retrievers import AmazonKendraRetriever
from langchain.chains import RetrievalQA

S3_BUCKET_NAME = os.environ["S3_BUCKET_NAME"]
REGION = os.environ['AWS_REGION']
KENDRA_INDEX_ID = os.getenv("KENDRA_INDEX_ID", None)
#BEDROCK_ENDPOINT_URL = os.getenv("BEDROCK_ENDPOINT_URL", None)
PROMPT_TEMPLATE = os.environ["PROMPT_TEMPLATE_CLAUDE"]

# Initialize the Bedrock client
#BEDROCK_CLIENT = boto3.client("bedrock", REGION, endpoint_url=BEDROCK_ENDPOINT_URL)
BEDROCK_CLIENT = boto3.client("bedrock")

# Define a function to build the chain using the provided model ID and arguments
def build_chain(modelId, model_args):
    llm = Bedrock(client=BEDROCK_CLIENT, model_id=modelId, verbose=True, model_kwargs=model_args)
    retriever = AmazonKendraRetriever(index_id=KENDRA_INDEX_ID)

    # Read the prompt template from S3 bucket
    s3 = boto3.resource('s3')
    obj = s3.Object(S3_BUCKET_NAME, PROMPT_TEMPLATE) 
    prompt_template = obj.get()['Body'].read().decode('utf-8')

    PROMPT = PromptTemplate(
        template=prompt_template, input_variables=["context", "question"]
    )
    chain_type_kwargs = {"prompt": PROMPT}
    
    return RetrievalQA.from_chain_type(
        llm=llm, 
        chain_type="stuff", 
        retriever=retriever, 
        chain_type_kwargs=chain_type_kwargs,
        return_source_documents=True
    )

# Define a function to run the chain and handle exceptions
def run_chain(chain, prompt: str, history=None):
    if history is None:
        history = []

    try:
        result = chain(prompt)
        # To make it compatible with chat samples
        return {
            "answer": result['result'],
            "source_documents": result['source_documents']
        }
    except Exception as e:
        # Raise a custom exception if needed
        raise Exception("An error occurred in run_chain: " + str(e))

# Lambda function entry point
def lambda_handler(event, context):
    # Print environment variables and event details
    print(f"boto3-version: {boto3.__version__}")
    print('kendra index:', KENDRA_INDEX_ID)
    print('S3_BUCKET_NAME:', S3_BUCKET_NAME)
    
    print('body of the input', json.loads(event["body"]))
    # Parse event body
    event_body = json.loads(event["body"])
    query = event_body["query"]
    print(f"query: {query}")

    list = BEDROCK_CLIENT.list_foundation_models()
    print('list of model:', list)

    # Extract model parameters
    modelId = event_body["model_id"]
    temp = event_body["temperature"]
    maxTokens = event_body["max_tokens"]
    print(f"selected model id: {modelId}")

    # Determine the maxTokenAttribute based on modelId
    maxTokenAttribute = 'maxTokenCount'
    # Define model arguments
    model_args = {
        #maxTokenCount: int(maxTokens),
        #"temperature": float(temp),
    }
    if modelId == 'amazon.titan-tg1-large':
        model_args = {
            "maxTokenCount": int(maxTokens),
            "temperature": float(temp),
        }
        PROMPT_TEMPLATE = os.environ["PROMPT_TEMPLATE_TITAN"]
    elif modelId == 'anthropic.claude-v2':
        model_args = {
            "max_tokens_to_sample": int(maxTokens),
            "temperature": float(temp)
        }
        PROMPT_TEMPLATE = os.environ["PROMPT_TEMPLATE_CLAUDE"]
    else:
        modelId == 'amazon.titan-tg1-large'
        PROMPT_TEMPLATE = os.environ["PROMPT_TEMPLATE_CLAUDE"]


    print('model_args', model_args)
    print('PROMPT_TEMPLATE:', PROMPT_TEMPLATE)

    
    # Run the chain and handle exceptions
    try:
        # Build the chain
        chain = build_chain(modelId, model_args)
        
        #Run the chain
        result = run_chain(chain, query)
        print('Answer', result['answer'])
    
        source_docs = []
        if 'source_documents' in result:
            print('Sources:')
            for d in result['source_documents']:
                print(d.metadata['source'])
                source_docs.append(d.metadata['source'])

        output = {"answer": result['answer'], "source_documents": source_docs}
        
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "*",
            },
            "body": json.dumps(output)
        }
    except Exception as e:
        # Print the error trace
        traceback.print_exc()

        # Handle exceptions and provide an error response
        error_message = str(e)
        error_response = {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "*",
            },
            "body": json.dumps({"error": error_message})
        }
        return error_response
