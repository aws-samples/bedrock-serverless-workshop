import coloredlogs
import logging
import os
import json
import boto3
import traceback

from langchain.embeddings import BedrockEmbeddings
from langchain.vectorstores import OpenSearchVectorSearch
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain.retrievers import AmazonKendraRetriever
from langchain.llms.bedrock import Bedrock

coloredlogs.install(fmt='%(asctime)s %(levelname)s %(message)s', datefmt='%H:%M:%S', level='INFO')
logging.basicConfig(level=logging.INFO) 
logger = logging.getLogger(__name__)

S3_BUCKET_NAME = os.environ["S3_BUCKET_NAME"]
KENDRA_INDEX_ID = os.getenv("KENDRA_INDEX_ID", None)
REGION = os.getenv('AWS_REGION', 'us-west-2')


def get_bedrock_client():
    bedrock_client = boto3.client("bedrock-runtime", region_name=REGION)
    return bedrock_client

def create_bedrock_llm(bedrock_client, model_version_id, model_args):
    bedrock_llm = Bedrock(
        model_id=model_version_id, 
        client=bedrock_client,
        model_kwargs=model_args,
        verbose=True, 
        )
    return bedrock_llm

def create_langchain_vector_embedding_using_bedrock(bedrock_client, bedrock_embedding_model_id):
    bedrock_embeddings_client = BedrockEmbeddings(
        client=bedrock_client,
        model_id=bedrock_embedding_model_id)
    return bedrock_embeddings_client
    

def lambda_handler(event, context):
    logging.info(f"Event is: {event}")
    # Parse event body
    event_body = json.loads(event["body"])
    question = event_body["query"]
    logging.info(f"Query is: {question}")
    
    
    try:

        #bedrock_embedding_model_id = args.bedrock_embedding_model_id

        bedrock_model_id = event_body["model_id"]
        temperature = event_body["temperature"]
        maxTokens = event_body["max_tokens"]
        logging.info(f"selected model id: {bedrock_model_id}")
        
        model_args = {}
        
        PROMPT_TEMPLATE = 'prompt-engineering/claude-prompt-template.txt'
        if bedrock_model_id == 'anthropic.claude-v2':
            model_args = {
                "max_tokens_to_sample": int(maxTokens),
                "temperature": float(temperature),
                "top_k": 50,
                "top_p": 0.1
            }
            PROMPT_TEMPLATE = 'prompt-engineering/claude-prompt-template.txt'
        elif bedrock_model_id == 'anthropic.claude-3-sonnet-20240229-v1:0':
            model_args = {
                "anthropic_version": "bedrock-2023-05-31",
                "temperature": float(temperature),
                "top_k": 250
            }
            PROMPT_TEMPLATE = 'prompt-engineering/claude-prompt-template.txt'
        elif bedrock_model_id == 'amazon.titan-text-express-v1':
            model_args = {
                "maxTokenCount": int(maxTokens),
                "temperature": float(temperature),
                "topP":1
            }
            PROMPT_TEMPLATE = 'prompt-engineering/titan-prompt-template.txt'
        elif bedrock_model_id == 'ai21.j2-mid-v1' or bedrock_model_id == 'ai21.j2-ultra-v1':
            model_args = {
                "maxTokens": int(maxTokens),
                "temperature": float(temperature),
                "topP":1
            }
            PROMPT_TEMPLATE = 'prompt-engineering/jurassic2-prompt-template.txt'
        elif bedrock_model_id == 'meta.llama2-13b-chat-v1':
            model_args = {
                "max_gen_len": int(maxTokens),
                "temperature": float(temperature),
                "top_p":0.9
            }
            PROMPT_TEMPLATE = 'prompt-engineering/llama-prompt-template.txt'
        elif bedrock_model_id == 'mistral.mistral-7b-instruct-v0:2':
            model_args = {
                "max_tokens": int(maxTokens),
                "temperature": float(temperature),
                "top_p":0.9,
                "top_k":50
            }
            PROMPT_TEMPLATE = 'prompt-engineering/llama-prompt-template.txt'
        else:
            model_args = {
                "max_tokens_to_sample": int(maxTokens),
                "temperature": float(temperature)
            }
        
        logging.info(f"Model orgs: {model_args}")

        # Read the prompt template from S3 bucket
        s3 = boto3.resource('s3')
        obj = s3.Object(S3_BUCKET_NAME, PROMPT_TEMPLATE) 
        prompt_template = obj.get()['Body'].read().decode('utf-8')
        logging.info(f"prompt: {prompt_template}")

        PROMPT = PromptTemplate(
            template=prompt_template, input_variables=["context", "question"]
        )

        #Create bedrock llm object
        bedrock_client = get_bedrock_client()
        bedrock_llm = create_bedrock_llm(bedrock_client, bedrock_model_id, model_args)
        #bedrock_embeddings_client = create_langchain_vector_embedding_using_bedrock(bedrock_client, bedrock_embedding_model_id)
        
        logging.info(f"Starting the chain with KNN similarity using Amazon Kendra, Bedrock FM {bedrock_model_id}")
        qa = RetrievalQA.from_chain_type(llm=bedrock_llm, 
                                    chain_type="stuff", 
                                    retriever=AmazonKendraRetriever(index_id=KENDRA_INDEX_ID),
                                    return_source_documents=True,
                                    chain_type_kwargs={"prompt": PROMPT, "verbose": False},
                                    verbose=False)
        
        response = qa(question, return_only_outputs=True)
        
        source_documents = response.get('source_documents')
        source_docs = []
        for d in source_documents:
            source_docs.append(d.metadata['source'])
        
        output = {"answer": response.get('result'), "source_documents": source_docs}

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
        print('Error: ' + str(e))
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

